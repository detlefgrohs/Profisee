import json, time
from datetime import datetime, timezone
from Profisee.Restful import API
from Profisee.Restful.GetOptions import GetOptions
from Profisee.Common import Common

instance_name = "Local"
settings = json.load(open(r"settings.json"))[instance_name]

profisee_url = settings.get("ProfiseeUrl", None)
client_id = settings.get("ClientId", None)
verify_ssl = settings.get("VerifySSL", True)

print(f"Using instance '{instance_name}' with ProfiseeUrl '{profisee_url}', ClientId '{client_id}', VerifySSL '{verify_ssl}'")

api = API(profisee_url, client_id, verify_ssl)



def RunConnectBatch(activity_type: str, service_name: str, strategy_name: str, sleep_time:int = 15) -> dict:
    print(f"Running Connect Batch for strategy '{strategy_name}'")
    since_datetime = datetime.now(timezone.utc)
    response = api.RunConnectBatch(strategy_name)

    get_options = GetOptions()
    get_options.Filter = f"[ActivityType] eq '{activity_type}' and [Service] eq '{service}' and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"

    first_activity_datetime = None
    was_successful = False

    while True:
        monitor_activities = api.GetMonitorActivities(get_options)

        # Now apply the name filter since we can't see to do it as part of the get_options.filter
        for index, monitor_activity in enumerate(monitor_activities):
            activity_type = Common.Get(monitor_activity, "Name", "")
            if strategy_name not in activity_type:
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

        time.sleep(sleep_time)
    
    return {
        "FirstActivityDateTime": first_activity_datetime,
        "ElapsedTime": (datetime.now() - first_activity_datetime),
        "NumberOfActivities": len(monitor_activities),
        "WasSuccessful": was_successful,
        "Activities": monitor_activities
    }


activity_type = "Database Export Activity"
service = "Connect"
strategy_name = "SQL Server [DQParent] Export [dbo].[tbl_DQParent]"

response = RunConnectBatch(activity_type, service, strategy_name)

print(f"First activity found at {response['FirstActivityDateTime'].strftime('%Y-%m-%d %H:%M:%S')}, total duration {response['ElapsedTime']}")
if response['WasSuccessful']:
    print("All activities completed successfully")
else:
    print("Some activities did not complete successfully")

print()    

strategy_name = "SQL Server [DQChild] Export [dbo].[tbl_DQChild]"

response = RunConnectBatch(activity_type, service, strategy_name)

print(f"First activity found at {response['FirstActivityDateTime'].strftime('%Y-%m-%d %H:%M:%S')}, total duration {response['ElapsedTime']}")
if response['WasSuccessful']:
    print("All activities completed successfully")
else:
    print("Some activities did not complete successfully")
