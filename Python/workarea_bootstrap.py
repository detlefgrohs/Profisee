import os, json

from Profisee.Restful import API, Entity, Attribute
from Profisee.Common import Common
from Profisee.Restful.Enums import AttributeType, AttributeDataType


if os.path.exists(r"settings.json"):
    settings = json.load(open(r"settings.json"))
elif os.path.exists(r"Python/settings.json"):
    settings = json.load(open(r"Python/settings.json"))
elif os.path.exists(r"_Internal/settings.json"):
    settings = json.load(open(r"_Internal/settings.json"))
else:
    print("You must provide a settings.json file with the ProfiseeUrl, ClientId.")
    exit(1)

profisee_url = Common.Get(settings, "ProfiseeUrl", None)
client_id = Common.Get(settings, "ClientId", None)
verify_ssl = Common.Get(settings, "VerifySSL", True)

api = API(profisee_url, client_id, verify_ssl)

orchestration_entity_name = Common.Get(settings, "OrchestrationEntityName", "OrchestrationA")
orchestration_step_entity_name = f"{orchestration_entity_name}Step"
orchestration_log_entity_name = f"{orchestration_entity_name}Log"

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
    
    api.CreateEntity(Entity(orchestration_log_entity_name, True, 100000000).to_Entity())
    api.CreateAttributes([
        Attribute(orchestration_log_entity_name, orchestration_entity_name, AttributeType.Domain, AttributeDataType.Text, domain=orchestration_entity_name).to_Attribute(),
        Attribute(orchestration_log_entity_name, orchestration_step_entity_name, AttributeType.Domain, AttributeDataType.Text, domain=orchestration_step_entity_name).to_Attribute(),
        Attribute(orchestration_log_entity_name, "LogLevel", AttributeType.FreeForm, AttributeDataType.Text, 200).to_Attribute(),
        Attribute(orchestration_log_entity_name, "Message", AttributeType.FreeForm, AttributeDataType.Text, 4000).to_Attribute(),
    ])
    
else:
    print(f"Base Entity Name '{orchestration_entity_name}' already exists. No action taken. You can delete the entities if you want to re-bootstrap.")


