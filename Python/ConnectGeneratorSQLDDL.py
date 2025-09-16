import logging, json, os, argparse
from Profisee import Restful

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info(f"Running {__file__}")

class ConnectGeneratorSQLDDL():
    def __init__(self, profisee_settings: dict, schema_name: str, table_name_format: str, only_entity_names: list) -> None:
        self.profisee_settings = profisee_settings
        self.schema_name = schema_name
        self.table_name_format = table_name_format
        self.only_entity_names = only_entity_names

    def generate(self) -> None:
        print(f"Connecting to '{self.profisee_settings["ProfiseeUrl"]}'")
        logger.info(f"Connecting to '{self.profisee_settings["ProfiseeUrl"]}'")
        api = Restful.API(self.profisee_settings["ProfiseeUrl"], self.profisee_settings["ClientId"], verify_ssl= False)

        entities = api.GetEntities()

        entity_names = []
        entity_names.extend(entity["identifier"]["name"] for entity in entities)
        entity_names = sorted(entity_names)
        
        ddl_content = ""

        for entity_name in filter(lambda entity_name : not self.only_entity_names or entity_name.lower() in map(str.lower, self.only_entity_names), entity_names):
            table_name = self.table_name_format.format(entity_name=entity_name)
            print(f"-- Generating DDL for entity '{entity_name}' into table '{table_name}'")
            
            ddl_statement = f"""
        CREATE TABLE [{self.schema_name}].[{table_name}] (
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
            
            ddl_statement += f""",
        CONSTRAINT [PK_{table_name}_Code] PRIMARY KEY CLUSTERED
        (
            [Code] ASC
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
        ) ON [PRIMARY]
        GO"""
            print(ddl_statement)
            ddl_content += f"\n{ddl_statement}\n"
            logger.info(ddl_statement)

        with open("SQL Server DDL.sql", "w") as ddl_file:
            ddl_file.write(ddl_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SQL DDL.")
    parser.add_argument("--instance", type=str, default="Local", help="The instance name to use from settings.json")
    parser.add_argument("--schema_name", type=str, default="dbo", help="The schema to use for table names")
    parser.add_argument("--table_name_format", type=str, default="tbl_{entity_name}", help="The format for table names")
    parser.add_argument("--only_entity_names", type=str, nargs='*', default=["test"], help="List of entity names to include (if empty, all entities are included)")

    args = parser.parse_args()
    
    instance_name = args.instance
    schema_name = args.schema_name
    table_name_format = args.table_name_format
    only_entity_names = args.only_entity_names
    
    logger.info(f"Using instance '{instance_name}'")
    logger.info(f"Using schema_name '{schema_name}'")
    logger.info(f"Using table_name_format '{table_name_format}'")
    logger.info(f"Using only_entity_names '{only_entity_names}'")

    with open('settings.json', 'r') as file: settings = json.load(file)
    profisee_settings = settings[instance_name]

    logger.info(f"Settings for instance '{instance_name}': {profisee_settings}")

    connect_generate_sql_ddl = ConnectGeneratorSQLDDL(profisee_settings, schema_name, table_name_format, only_entity_names)
    connect_generate_sql_ddl.generate()