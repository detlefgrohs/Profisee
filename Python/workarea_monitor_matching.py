import json, time
from datetime import datetime, timezone
from Profisee.Restful import API
from Profisee.Restful.GetOptions import GetOptions
from Profisee.Restful.Enums import ProcessActions
from Profisee.Common import Common


instance_name = "Local"
settings = json.load(open(r"settings.json"))[instance_name]

profisee_url = settings.get("ProfiseeUrl", None)
client_id = settings.get("ClientId", None)
verify_ssl = settings.get("VerifySSL", True)

print(f"Using instance '{instance_name}' with ProfiseeUrl '{profisee_url}', ClientId '{client_id}', VerifySSL '{verify_ssl}'")

api = API(profisee_url, client_id, verify_ssl)

activity_type = "Clustering %26 Survivorship"
service = "Matching"
strategy_name = "MatchingTest"
since_datetime = datetime.now(timezone.utc)


response = api.ProcessMatchingActions(strategy_name, ProcessActions.MatchingAndSurvivorship)


get_options = GetOptions()
get_options.Filter = f"[ActivityType] eq '{activity_type}' and [Service] eq '{service}' and contains([Name], '{strategy_name}') and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"

# print(get_options.Filter)

complete = False

while not complete:
    monitor_activities = api.GetMonitorActivities(get_options)
    
    for activity in monitor_activities:
        activity_id = Common.Get(activity, "Id", "")
        status = Common.Get(activity, "Status", "")
        activity_name = Common.Get(activity, "Name", "")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : Activity '{activity_id}' '{activity_name}' is '{status}'")

        if status in ["Completed", "Failed", "Cancelled"]:
            complete = False
        
    time.sleep(5)

