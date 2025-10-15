import os, sys
from datetime import datetime, timezone
import threading
from typing import Any
import json, time, random
import argparse
from functools import wraps
import urllib.parse

from Profisee.Restful import API, Entity, Attribute
from Profisee.Restful import GetOptions
from Profisee.Common import Common
from Profisee.Restful.Enums import AttributeType, AttributeDataType, ProcessActions, get_enum_from_string

class Orchestration:
    def __init__(self, api: API, orchestration_entity_name: str = "Orchestration") -> None:
        self.API = api
        self.results = []
        self.orchestration_entity_name = orchestration_entity_name
        self.orchestration_step_entity_name = f"{orchestration_entity_name}Step"
        self.orchestration_log_entity_name = f"{orchestration_entity_name}Log"
        self.what_if = False

        self.get_orchestration_settings()
        self.ignore_response_list = [ (400, "no records were found") ]

    def get_orchestration_settings(self) -> None:
        self.min_log_level = "debug"
        self.activity_polling_interval = 15 # seconds

        if (settings_record := self.API.GetRecord(self.orchestration_entity_name, "z_Settings")):
            settings = self.parse_json(Common.Get(settings_record, "Parameters", "{}"))
            if settings is not None:
                self.min_log_level = Common.Get(settings, "MinLogLevel", "INFO").lower()
                self.activity_polling_interval = Common.Get(settings, "ActivityPollingInterval", 15) # seconds
                        
        print(f"Orchestration settings: MinLogLevel={self.min_log_level}, ActivityPollingInterval={self.activity_polling_interval}")

    def LogFunction(func) :
        @wraps(func)
        def out(*args, **kwargs) :
            parameterList = []        
            if args != None : 
                args1 = args[1:] # To strip off self, need a better way to do this to make it generic...
                parameterList.append(str(args1).strip('(),'))
            if kwargs: parameterList.append(str(kwargs).strip('{}'))
            parameters = ', '.join(parameterList)

            self = args[0] # First argument is self for class methods
            orchestration_code = None
            orchestration_step_code = None
            if func.__name__ != "orchestrate": # all other methods should have these as args
                orchestration_code = args[1]
                orchestration_step_code = args[2]
                
            self.LogToProfisee(orchestration_code, orchestration_step_code, "DEBUG", f"Calling {func.__name__}({parameters})")

            return_value = func(*args, **kwargs)

            self.LogToProfisee(orchestration_code, orchestration_step_code, "DEBUG", f"Finished {func.__name__}({parameters}) with result: {return_value}")
            return return_value
        return out

    def parse_json(self, json_string: str) -> dict[str, Any]:
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            self.LogToProfisee(None, None, "ERROR", f"Error parsing JSON: {e}")
            return None

    def get_orchestration_steps(self, orchestration_code: str) -> list[dict[str, Any]]:
        options = GetOptions()
        options.Filter = f"[{self.orchestration_entity_name}] eq '{orchestration_code}'"
        options.OrderBy = "[StepNumber]"
        return self.API.GetRecords(self.orchestration_step_entity_name, options)

    def get_orchestration(self, orchestration_code: str) -> dict[str, Any]:
        orchestration = self.API.GetRecord(self.orchestration_entity_name, orchestration_code)

        return (orchestration, self.parse_json(Common.Get(orchestration, "Parameters", "{}")) if orchestration else None)

    @LogFunction
    def orchestrate(self, orchestration_code: str) -> dict[str, Any]:
        
        (orchestration, orchestration_parameters) = self.get_orchestration(orchestration_code)        
        if orchestration is None or orchestration_parameters is None:
            return {
                "Error": True,
                "Message": f"Orchestration '{orchestration_code}' not found or has invalid parameters."
            }        
        threaded = Common.Get(orchestration_parameters, "Mode", "Sequential") == "Concurrent"
        abort_on_error = Common.Get(orchestration_parameters, "ErrorHandling", "Abort") == "Abort"

        self.LogToProfisee(orchestration_code, None, "INFO", f"Starting orchestration '{orchestration_code}' with parameters {orchestration_parameters}; running in {'threaded' if threaded else 'sequential'} mode.")

        threads = []
        self.results = []
        
        for step in self.get_orchestration_steps(orchestration_code):
            strategy_name = Common.Get(step, "Name", "")
            orchestration_step_code = Common.Get(step, "Code", "")
            process_type = Common.Get(step, "ProcessType", "")
            parameters_json = Common.Get(step, "Parameters", {})
            parameters = self.parse_json(parameters_json)
            
            if parameters is None:
                return {
                    "Error": True,
                    "Message": f"Orchestration '{orchestration_code}' step '{orchestration_step_code}' has invalid JSON parameters: {parameters_json}"
                }
            
            if Common.Get(parameters, "Enabled", True):
                if threaded:
                    thread = threading.Thread(target=self.run, args=(orchestration_code, orchestration_step_code, strategy_name, process_type, parameters))
                    threads.append(thread)
                    thread.start()
                else:
                    result = self.run(orchestration_code, orchestration_step_code, strategy_name, process_type, parameters)
                    if Common.Get(result, "Error", False) and abort_on_error:
                        self.LogToProfisee(orchestration_code, None, "ERROR", f"Orchestration '{orchestration_code}' failed on step '{orchestration_step_code}' '{strategy_name}' with process type '{process_type}' and parameters {parameters}.")
                        break
            else:
                self.LogToProfisee(orchestration_code, orchestration_step_code, "INFO", f"Skipping disabled orchestration step '{orchestration_step_code}' '{strategy_name}'.")

        if threaded: map(lambda thread: thread.join(), threads) # Wait for all threads to complete

        if overall_error := any(Common.Get(result, "Error", False) for result in self.results):
            self.LogToProfisee(orchestration_code, None, "ERROR", f"Orchestration '{orchestration_code}' completed with errors.")
        else:
            self.LogToProfisee(orchestration_code, None, "INFO", f"Orchestration '{orchestration_code}' complete.")
        
        return {
            "Orchestration": orchestration_code,
            "Error": overall_error,
            "Results": self.results
        }
        

    @LogFunction
    def run(self, orchestration_code:str, orchestration_step_code: str, name: str, process_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        
        since_datetime = datetime.now(timezone.utc)
        run_errored = False

        start_process_result = self.start_process(orchestration_code, orchestration_step_code, name, process_type, parameters)
        
        if Common.Get(start_process_result, "Error", False) :
            run_errored = True            
        elif not Common.Get(start_process_result, "ContinueToMonitor", False) :
            wait_for_completion_result = self.wait_for_completion(orchestration_code, orchestration_step_code, name, process_type, parameters, since_datetime)
            run_errored = Common.Get(wait_for_completion_result, "Error", False)
        
        result = {
            "Orchestration": orchestration_code,
            "OrchestrationStep": orchestration_step_code,
            "Name": name,
            "ProcessType": process_type,
            "Parameters": parameters,
            "Error": run_errored,
            "Message": f"Running orchestration step '{process_type}' '{name}' with {parameters}..."
        }
        self.results.append(result)
        return result

    @LogFunction
    def start_process(self, orchestration_code:str, orchestration_step_code: str, name: str, process_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        
        match process_type.lower():
            case "connect":
                return self.start_process_connect(orchestration_code, orchestration_step_code, name, parameters)
            case "matching":
                return self.start_matching_process(orchestration_code, orchestration_step_code, name, parameters)
            case _:
                return {
                    "Error": True,
                    "Message": f"Unknown process type '{process_type}' for orchestration step '{name}'."
                }

    def can_ignore_error(self, response : dict[str, Any]) -> bool:
        return any(
            item[0] == Common.Get(response, "StatusCode") and item[1] in Common.Get(response, "Error")
            for item in self.ignore_response_list
        )

    @LogFunction
    def start_process_connect(self, orchestration_code:str, orchestration_step_code: str, strategy_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if self.what_if:
            self.LogToProfisee(orchestration_code, orchestration_step_code, "INFO", f"WHATIF: Would run Connect Batch for strategy '{strategy_name}'")
            return {
                "Error": False,
                "response": None
            }
        
        response = self.API.RunConnectBatch(strategy_name, Common.Get(parameters, "Filter"))
        is_error = False
        error_was_ignored = False
        
        if self.API.StatusCode != 200:
            if self.can_ignore_error(response) :
                error_was_ignored = True
                self.LogToProfisee(orchestration_code, orchestration_step_code, "WARNING", f"Started Connect Batch for strategy '{strategy_name}'. StatusCode: {self.API.StatusCode}, Response: {self.API.LastResponse.text}")
            else :
                is_error = True
                self.LogToProfisee(orchestration_code, orchestration_step_code, "ERROR", f"Failed to start Connect Batch for strategy '{strategy_name}'. StatusCode: {self.API.StatusCode}, Response: {self.API.LastResponse.text}")
            
        return {
            "Error": is_error,
            "ContinueToMonitor" : error_was_ignored,
            "response": response
        }
                
    @LogFunction
    def start_matching_process(self, orchestration_code:str, orchestration_step_code: str, strategy_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if self.what_if:
            self.LogToProfisee(orchestration_code, orchestration_step_code, "INFO", f"WHATIF: Would run Matching for strategy '{strategy_name}'")
            return {
                "Error": False,
                "response": None
            }
        
        process_action = get_enum_from_string(ProcessActions, Common.Get(parameters, "ProcessAction", "MatchingOnly"))    
        response = self.API.ProcessMatchingActions(strategy_name, process_action)

        if self.API.StatusCode != 200:
            self.LogToProfisee(orchestration_code, orchestration_step_code, "ERROR", f"Failed to start Matching for strategy '{strategy_name}'. StatusCode: {self.API.StatusCode}, Response: {self.API.LastResponse.text}")
            
        return {
            "Error": self.API.StatusCode != 200,
            "response": response
        }

    def get_activity_type_for_process_type(self, process_type: str, parameters: dict[str, Any]) -> str:
        match process_type.lower():
            case "connect":
                return Common.Get(parameters, "ActivityType", "Connect Strategy Execution")
            case "matching":
                return Common.Get(parameters, "ActivityType", "Clustering & Survivorship")           
            case _:
                return None
            
    @LogFunction
    def wait_for_completion(self, orchestration_code:str, orchestration_step_code: str, name: str, process_type: str, parameters: dict[str, Any], since_datetime: datetime) -> dict[str, Any]:
        if self.what_if:
            self.LogToProfisee(orchestration_code, orchestration_step_code, "INFO", f"WHATIF: Would wait for completion of process type '{process_type}' for orchestration step '{name}'")
            return {
                "FirstActivityDateTime": datetime.now(),
                "ElapsedTime": (datetime.now() - datetime.now()),
                "Error": False,
                "Activities": []
            }
        
        first_activity_datetime = None
        was_successful = False
        
        get_options = GetOptions()
        # get_options.Filter = f"contains([Name], '{name}') and [ActivityType] eq '{self.get_activity_type_for_process_type(process_type, parameters)}' and [Service] eq '{process_type}' and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        get_options.Filter = f"[ActivityType] eq '{self.get_activity_type_for_process_type(process_type, parameters)}' and [Service] eq '{process_type}' and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        while True:
            monitor_activities = self.API.GetMonitorActivities(get_options)

            # Now apply the name filter since we can't seem to do it as part of the get_options.filter
            for index, monitor_activity in enumerate(monitor_activities):
                activity_type = Common.Get(monitor_activity, "Name", "")
                if name not in activity_type:
                    del monitor_activities[index]
        
            if monitor_activities:
                if first_activity_datetime is None:
                    first_activity_datetime = datetime.now()

                number_of_not_running = 0
                number_of_succeeded = 0
                
                for activity in monitor_activities:
                    status = Common.Get(activity, "Status", "")
                    
                    if status not in ["Running"]:
                        number_of_not_running += 1
                        
                    if status == 'Succeeded':
                        number_of_succeeded += 1        
                                        
                if len(monitor_activities) > 0 and len(monitor_activities) == number_of_not_running:
                    if number_of_succeeded == len(monitor_activities):           
                        was_successful = True
                    break

            time.sleep(self.activity_polling_interval)

        return {
            "FirstActivityDateTime": first_activity_datetime,
            "ElapsedTime": (datetime.now() - first_activity_datetime),
            "Error": not was_successful,
            "Activities": monitor_activities
        }

    def should_log(self,log_level: str) -> bool:
        log_levels = { "debug":0, "info":1, "warning":2, "error":3, "critical":4 }
        return log_levels[log_level.lower()] >= log_levels[self.min_log_level.lower()]
    
    def LogToProfisee(self, orchestration_code: str, orchestration_step_code:str, log_level: str, message: str) -> None:
        if self.should_log(log_level):
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{log_level}] : {orchestration_code} {orchestration_step_code} {message}")
            self.API.MergeRecord(self.orchestration_log_entity_name, {
                self.orchestration_entity_name: orchestration_code,
                self.orchestration_step_entity_name: orchestration_step_code,
                "LogLevel": log_level,
                "Message": message})

    @staticmethod
    def BootstrapOrchestrationEntities(api: API, orchestration_entity_name: str) -> dict[str, Any]:                    
        api.GetEntity(orchestration_entity_name)
        if api.StatusCode == 404:
            print(f"Bootstrapping Entities for Orchestration Base Entity Name = '{orchestration_entity_name}'")
            
            api.CreateEntity(Entity(orchestration_entity_name).to_Entity())
            api.CreateAttributes([
                Attribute(orchestration_entity_name, "Parameters", AttributeType.FreeForm, AttributeDataType.Text, 4000).to_Attribute()
            ])
            
            api.MergeRecords(orchestration_entity_name, [{
                "Name" : "z_Settings",
                "Code" : "z_SETTINGS",
                "Parameters" : '{ "MinLogLevel" : "Debug", "ActivityPollingInterval" : 5 }'
            }, 
            {
                "Name" : "Sample",
                "Code" : "SAMPLE",
                "Parameters" : '{ "Mode" :"Sequential", "ErrorHandling" : "Abort" }'
            }])
            
            orchestration_step_entity_name = f"{orchestration_entity_name}Step"
            api.CreateEntity(Entity(orchestration_step_entity_name, True, 100000000).to_Entity())
            api.CreateAttributes([
                Attribute(orchestration_step_entity_name, orchestration_entity_name, AttributeType.Domain, AttributeDataType.Text, domain=orchestration_entity_name).to_Attribute(),
                Attribute(orchestration_step_entity_name, "StepNumber", AttributeType.FreeForm, AttributeDataType.Number, 0).to_Attribute(),
                Attribute(orchestration_step_entity_name, "ProcessType", AttributeType.FreeForm, AttributeDataType.Text, 200).to_Attribute(),
                Attribute(orchestration_step_entity_name, "Parameters", AttributeType.FreeForm, AttributeDataType.Text, 4000).to_Attribute()
            ])
            
            api.MergeRecords(orchestration_step_entity_name, [{
                "Name" : "SQL Server [DQParent] Export [dbo].[tbl_DQParent]",
                orchestration_entity_name : "SAMPLE",
                "StepNumber" : 1,
                "ProcessType" : "Connect",
                "Parameters" : '{ "ActivityType" : "Database Export Activity" }'
            }, 
            {
                "Name" : "SQL Server [DQChild] Export [dbo].[tbl_DQChild]",
                orchestration_entity_name : "SAMPLE",
                "StepNumber" : 2,
                "ProcessType" : "Connect",
                "Parameters" : '{ "ActivityType" : "Database Export Activity", "Enabled" : false }'
            }])
            
            orchestration_log_entity_name = f"{orchestration_entity_name}Log"
            api.CreateEntity(Entity(orchestration_log_entity_name, True, 100000000).to_Entity())
            api.CreateAttributes([
                Attribute(orchestration_log_entity_name, orchestration_entity_name, AttributeType.Domain, AttributeDataType.Text, domain=orchestration_entity_name).to_Attribute(),
                Attribute(orchestration_log_entity_name, orchestration_step_entity_name, AttributeType.Domain, AttributeDataType.Text, domain=orchestration_step_entity_name).to_Attribute(),
                Attribute(orchestration_log_entity_name, "LogLevel", AttributeType.FreeForm, AttributeDataType.Text, 200).to_Attribute(),
                Attribute(orchestration_log_entity_name, "Message", AttributeType.FreeForm, AttributeDataType.Text, 4000).to_Attribute(),
            ])
            
        else:
            print(f"Base Entity Name '{orchestration_entity_name}' already exists. No action taken. You can delete the entities if you want to re-bootstrap.")

# Main entry point
if __name__ == "__main__":    
    # Do the search for the settings.json file in multiple locations
    # settings.json for running from the command line in the proper folder
    # Python/settings.json for debugging in VS Code
    # _Internal/settings.json for running inside a PyInstaller executable
    if os.path.exists(r"settings.json"):
        settings = json.load(open(r"settings.json"))
    elif os.path.exists(r"Python/settings.json"):
        settings = json.load(open(r"Python/settings.json"))
    elif os.path.exists(r"_Internal/settings.json"):
        settings = json.load(open(r"_Internal/settings.json"))
    else:
        print("You must provide a settings.json file with the ProfiseeUrl, ClientId.")
        exit(1)

    orchestration_entity_name = Common.Get(settings, "OrchestrationEntityName", "Orchestration")
    
    parser = argparse.ArgumentParser(description="Orchestrate Profisee Processes.")
    parser.add_argument("--name", type=str, help=f"Name of Orchestration to run from {orchestration_entity_name} entity.")
    parser.add_argument("--bootstrap", action='store_true', help="If set, will create all of the necessary entities to run the orchestration.")
    parser.add_argument("--test", action='store_true', help="Test the connection to the Profisee API.")
    parser.add_argument("--whatif", action='store_true', help="If set, will not make any changes, but will show what would be done.")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    profisee_url = Common.Get(settings, "ProfiseeUrl", None)
    client_id = Common.Get(settings, "ClientId", None)
    verify_ssl = Common.Get(settings, "VerifySSL", True)

    api = API(profisee_url, client_id, verify_ssl)
    
    if args.test:
        print(f"Testing connection to ProfiseeUrl '{profisee_url}' with ClientId '{client_id}' and VerifySSL '{verify_ssl}'")
        result = api.GetEntities()
        if api.StatusCode == 200:
            print(f"Connection successful. StatusCode: {api.StatusCode}, Found: {len(result)} entities.")
            sys.exit(0)
        else:
            print(f"Connection failed. StatusCode: {api.StatusCode}, Response: {api.LastResponse.text}")
            sys.exit(1)
    
    if args.bootstrap:
        print("Bootstrapping the Orchestration entities...")
        result = Orchestration.BootstrapOrchestrationEntities(api, orchestration_entity_name)
        sys.exit(0)
                
                
    if not args.name:
        print("You must provide the name of the orchestration to run using --name")
        sys.exit(1)

    orchestration = Orchestration(api, orchestration_entity_name)
    orchestration.what_if = args.whatif
    result = orchestration.orchestrate(args.name)
    print(result)
    
    if Common.Get(result, "Error", False):
        sys.exit(1)
    sys.exit(0)