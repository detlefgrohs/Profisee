import json, time, os
from datetime import datetime, timezone
from pprint import pprint
from typing import Any

from Profisee.Restful import API
from Profisee.Restful.GetOptions import GetOptions
from Profisee.Common import Common
from Profisee.Restful.Theme import Theme

instance_name = "Local"

if os.path.exists(r"settings_private.json"):
    settings = json.load(open(r"settings_private.json"))
elif os.path.exists(r"Python/settings_private.json"):
    settings = json.load(open(r"Python/settings_private.json"))
elif os.path.exists(r"_Internal/settings_private.json"):
    settings = json.load(open(r"_Internal/settings_private.json"))
else:
    print("You must provide a settings.json file with the ProfiseeUrl, ClientId.")
    exit(1)

settings = settings[instance_name]

profisee_url = settings.get("ProfiseeUrl", None)
client_id = settings.get("ClientId", None)
verify_ssl = settings.get("VerifySSL", True)

print(f"Using instance '{instance_name}' with ProfiseeUrl '{profisee_url}', ClientId '{client_id}', VerifySSL '{verify_ssl}'")

api = API(profisee_url, client_id, verify_ssl)


ignore_response_list = [
    (400, "no records were found")
]

def can_ignore_error(response : dict[str, Any]) -> bool:
    global ignore_response_list

    return any(
        item[0] == Common.Get(response, "StatusCode") and item[1] in Common.Get(response, "Error")
        for item in ignore_response_list
    )




response = api.RunConnectBatch("SQL Server [dbo].[tbl_Test] Import [Test]")

pprint(response)
pprint(Common.Get(response, "StatusCode"))
pprint(Common.Get(response, "Error"))
pprint(can_ignore_error(response))


response = api.RunConnectBatch("SQL Server [dbo].[tbl_DQParent] Import [DQParent]")

pprint(response)
pprint(Common.Get(response, "StatusCode"))
pprint(Common.Get(response, "Error"))
pprint(can_ignore_error(response))
