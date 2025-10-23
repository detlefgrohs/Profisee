import json, time, os
from datetime import datetime, timezone
from Profisee.Restful import API
from Profisee.Restful.GetOptions import GetOptions
from Profisee.Common import Common
from Profisee.Restful.Theme import Theme

instance_name = "SK-Dev"

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

print(api.GetTheme("default"))

theme = Theme.from_Theme(api.GetTheme("default"))

print(theme.AccentFi)

print(theme.to_Theme())

print(api.GetThemes())