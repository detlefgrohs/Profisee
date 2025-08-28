import logging, json
from pathlib import Path
from Profisee import Restful
from Profisee.Common import Common

instance_name = "Local"

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info(f"Running {__file__}")

with open('settings.json', 'r') as file: settings = json.load(file)
profisee_settings = settings[instance_name]

print(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
logger.info(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
api = Restful.API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify = False)

entity_name = 'WorkareaAttributeChange'
attribute_name = 'StoreId'
temp_attribute_name = 'Temp_' + attribute_name

# A) Create New Attribute with ProperType
new_attribute = Restful.Attribute(entity_name, temp_attribute_name, dataType=Restful.Enums.AttributeDataType.Number)
new_attribute.Length = 0
api.CreateAttribute(new_attribute.to_Attribute())

if api.StatusCode != 200 :
    print(f"Failed to create {entity_name}:{temp_attribute_name}")
    print(api.LastResponse.json())
else :
    # B) Copy data from old Attribute to New Attribute
    updated_records = []
    getOptions = Restful.GetOptions()
    getOptions.PageSize = 10000 # More than enough to handle Store_Store records - Need to do this in pages for larger data sets

    for record in api.GetRecords(entity_name, getOptions) :
        updated_records.append({
            "Code" : Common.Get(record, "Code"),
            temp_attribute_name : Common.Get(record, attribute_name) # Any transformation will happen here. ie Trim etc...
        })
    api.MergeRecords(entity_name, updated_records)

    if api.StatusCode != 200 :
        print(f"Failed to copy data from {entity_name}:{attribute_name} to {temp_attribute_name}")
        print(api.LastResponse.json())
    else :
        # C) Remove/Rename Old Attribute (Renaming for now)
        api.ChangeAttributeName(entity_name, attribute_name, attribute_name + '_Archive')
        
        if api.StatusCode != 200 : 
            print(f"Failed to rename {entity_name}:{attribute_name} to {attribute_name + '_Archive'}")
            print(api.LastResponse.json())
        else :
            # D) Rename New Attribute 
            api.ChangeAttributeName(entity_name, temp_attribute_name, attribute_name)
            
            if api.StatusCode != 200 : 
                print(f"Failed to rename {entity_name}:{temp_attribute_name} to {attribute_name}")
                print(api.LastResponse.json())