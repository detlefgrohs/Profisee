import json, time, os
from datetime import datetime, timezone
from pprint import pprint
from typing import Any

from Profisee.Restful import API
from Profisee.Restful.GetOptions import GetOptions
from Profisee.Common import Common
from Profisee.Restful.Theme import Theme

from prettytable import PrettyTable

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

attributes = api.GetAttributes("Product_Product")

attributes = sorted(attributes, key=lambda x: Common.Get(x, "SortOrder"))

attributeSummary = []

for attribute in attributes :
    name = Common.Get(attribute, "Identifier.Name")
    attributeType = Common.Get(attribute, "AttributeType")
    dataType = Common.Get(attribute, "DataType")
    dataTypeInformation = Common.Get(attribute, "DataTypeInformation")
    domainEntityName = Common.Get(attribute, "DomainEntityId.Name")
    sortOrder = Common.Get(attribute, "SortOrder")
    
    typeInformation = "Unknown()"
    match attributeType, dataType :
        case 1, 1 :
            typeInformation = f"Text({dataTypeInformation})"
        case 1, 2 : 
            typeInformation = f"Number({dataTypeInformation})"
        case 1, 3 :
            typeInformation = "DateTime"
        case 1, 4 :
            typeInformation = "Date"
        case 2, 1 :
            typeInformation = f"DBA({domainEntityName})"
    
    attributeSummary.append({
        "Name" : name,
        # "AttributeType" : attributeType,
        # "DataType" : dataType,
        # "DataTypeInformation" : dataTypeInformation,
        # "DomainEntityName" : domainEntityName,
        "Type" : typeInformation,
        "Added" : "Yes" if sortOrder >= 20 else ""
    })


# pprint(attributeSummary

fromBrink = [
            "BrinkItemId",
            "SourceSystem",
            "AlternateId",
            "PLU",
            "Price",
            "RevenueCenter",
            "BrinkItemName"
            ]


table = PrettyTable()
table.field_names = [ "Name", "Type ", "Source", "Added", "____SourceFieldName____", "__________Notes_________" ]
for item in attributeSummary :
    table.add_row([item["Name"], item["Type"], "Brink" if item["Name"] in fromBrink else "", item["Added"], "", "" ])

print(table)

"""
 {'attributeType': 1,
  'auditInfo': {'createdDateTime': '2025-08-13T09:39:21.503Z',
                'createdUserId': {'id': 'ed223dbd-4b71-477d-a487-2ca1f07d7e97',
                                  'internalId': 16,
                                  'isReferenceValid': True,
                                  'name': 'restful.api@smoothieking.com'},
                'updatedDateTime': '2025-08-13T09:39:21.503Z',
                'updatedUserId': {'id': 'ed223dbd-4b71-477d-a487-2ca1f07d7e97',
                                  'internalId': 16,
                                  'isReferenceValid': True,
                                  'name': 'restful.api@smoothieking.com'}},
  'changeTrackingGroup': 0,
  'dataType': 1,
  'dataTypeInformation': 200,
  'defaultValue': None,
  'displayOrder': 23,
  'domainEntityIsFlat': False,
  'domainEntityIsSystemAware': False,
  'externalSystem': None,
  'fullyQualifiedName': None,
  'hasDefault': False,
  'identifier': {'entityId': {'id': 'fa47ff46-4425-463a-9298-dba07b438b32',
                              'internalId': 101,
                              'isReferenceValid': True,
                              'name': 'Product_Product'},
                 'id': 'ee212523-5753-469f-af96-f9bd3d1eee46',
                 'internalId': 1649,
                 'isReferenceValid': True,
                 'memberType': 1,
                 'modelId': {'id': 'b08af24d-4aa3-4d4f-a9cd-439d232b717e',
                             'internalId': 1,
                             'isReferenceValid': True,
                             'name': 'Maestro'},
                 'name': 'PrepaidItemType'},
  'integrationName': 'PrepaidItemType',
  'isAlwaysRequired': False,
  'isCascadeDeleteEnabled': False,
  'isClearOnClone': False,
  'isCode': False,
  'isIndexed': False,
  'isName': False,
  'isReadOnly': False,
  'isRestricted': False,
  'isSystem': False,
  'isUnique': False,
  'longDescription': None,
  'multiLevelContext': None,
  'permission': 2,
  'profiseePermision': 2,
  'sortOrder': 23}
"""