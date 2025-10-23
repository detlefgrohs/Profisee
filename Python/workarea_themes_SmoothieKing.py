import json, os
from Profisee.Restful import API
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

theme = Theme() # Load Default Theme

theme.BannerPrimary = (255,255,255)
theme.BannerFi = (62,19,17)
theme.BannerSecondary = (251,201,196)
theme.BannerPrimaryBg = (255,255,255)
theme.ContentSecondaryBg = (242,244,245)
theme.ContentSecondaryFi = (254,233,227)
theme.AccentBg = (144,24,35) # This was switched somehow :(
theme.AccentFi = (255,255,255) # This was switched somehow :(
theme.SelectedBg = (251,201,196)
theme.Hyperlink = (114,14,47)

print(theme.to_Theme())

print(api.UpdateTheme("default", theme.to_Theme()))

# https://support.profisee.com/wikis/profiseeplatform/updating_portal_themes_using_the_rest_api

# From : https://dev.azure.com/smoothieking/Enterprise-Data/_wiki/wikis/Enterprise-Data.wiki/122/Web-Portal-Theming
"""
{
      "bannerPrimary": "255,255,255",
      "bannerFi": "62, 19, 17",
      "bannerSecondary": "251, 201, 196",
      "contentPrimaryBg": "255, 255, 255",
      "contentPrimaryFi": "107, 114, 128",
      "contentSecondaryBg": "242, 244, 245",
      "contentSecondaryFi": "254, 233, 227",
      "accentBg": "144, 24, 35",
      "accentFi": "255, 255, 255",
      "selectedBg": "251, 201, 196",
      "hyperlink": "114, 14, 47",
}
"""

# Default Theme
"""
{
      "bannerPrimary": "255, 255, 255",
      "bannerFi": "27, 49, 65",
      "bannerSecondary": "32, 162, 223",
      "contentPrimaryBg": "255, 255, 255",
      "contentPrimaryFi": "107, 114, 128",
      "contentSecondaryBg": "243, 245, 246",
      "contentSecondaryFi": "27, 49, 65",
      "accentBg": "255, 255, 255",
      "accentFi": "44, 47, 53",
      "selectedBg": "210, 237, 249",
      "hyperlink": "19, 98, 134",
      "navStart": "16, 82, 112",
      "navEnd": "0, 135, 197",
}
"""