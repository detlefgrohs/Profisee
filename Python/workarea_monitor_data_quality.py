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

activity_type = "Entity Rule Evaluation"
service = "Data"
entity_name = "DQChild"
since_datetime = datetime.now(timezone.utc)
# since_datetime = datetime(2024, 6, 20, 12, 15, 0, tzinfo=timezone.utc)

get_options = GetOptions()
get_options.Filter = f"[ActivityType] eq '{activity_type}' and [Service] eq '{service}' and contains([Name], '{entity_name}') and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"

first_activity_datetime = None

while True:
    monitor_activities = api.GetMonitorActivities(get_options)

    number_of_succeeded = 0
    
    if not monitor_activities:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : No activities found")
        time.sleep(5)
        continue
    
    if first_activity_datetime is None:
        first_activity_datetime = datetime.now()
    
    for activity in monitor_activities:
        activity_id = Common.Get(activity, "Id", "")
        status = Common.Get(activity, "Status", "")
        activity_name = Common.Get(activity, "Name", "")
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : Activity '{activity_id}' '{activity_name}' is '{status}'")
        
        if status not in ["Running"]:
            number_of_succeeded += 1
        
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} : Found {len(monitor_activities)} activities, {number_of_succeeded} completed/failed/cancelled")        
            
    if len(monitor_activities) > 0 and len(monitor_activities) == number_of_succeeded:
        break

    time.sleep(5)

print("Done")
print(f"First activity found at {first_activity_datetime.strftime('%Y-%m-%d %H:%M:%S')}, total duration {(datetime.now() - first_activity_datetime)}")