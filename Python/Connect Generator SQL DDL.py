import logging, json, os
from Profisee import Restful

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

entities = api.GetEntities()

entity_names = []
entity_names.extend(entity["identifier"]["name"] for entity in entities)
entity_names = sorted(entity_names)
only_entity_names = [ "Test" ]

for entity_name in filter(lambda entity_name : not only_entity_names or entity_name in only_entity_names, entity_names):
    ddl_statement = f"""
CREATE TABLE [dbo].[tbl_{entity_name}] (
    [ID] [int] IDENTITY(1,1) NOT NULL,
    [Code] [varchar](250) NOT NULL,
    [Name] [varchar](250) NULL,
"""
    
    fields = []
    attributes = api.GetAttributes(entity_name)
    sorted_attributes = sorted(attributes, key = lambda attribute : attribute["sortOrder"])
    for attribute in sorted_attributes:
        #print(attribute)
        attribute_name = attribute["identifier"]["name"]
                
        if attribute_name not in ['Name', 'Code'] :
            attribute_type = attribute["attributeType"]
            data_type = attribute["dataType"]
            data_type_information = attribute["dataTypeInformation"]

            field_info = ""
            match attribute_type:
                case 1:
                    match data_type:
                        case 1: field_info = f"[varchar]({data_type_information})"
                        case 2: field_info = f"[decimal](26,{data_type_information})"
                        case 3: field_info =  "[datetime2](3)"
                        case 4: field_info =  "[date]"

                case 2:
                    field_info = f"[varchar]({data_type_information})" # for now DBAs are soft

                case _:
                    pass
        
            fields.append(f"    [{attribute_name}] {field_info} NULL")
    
    ddl_statement += """,
""".join(fields)
    
    ddl_statement += f"""
CONSTRAINT [PK_tbl_{entity_name}] PRIMARY KEY CLUSTERED
(
    [Code] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO"""
    print(ddl_statement)
    logger.info(ddl_statement)
