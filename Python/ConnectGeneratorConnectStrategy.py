import logging, json, os, uuid, argparse
from Profisee import Restful

instance_name = "Local"

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info(f"Running {__file__}")



class ConnectGeneratorConnectStrategy():
    def __init__(self, profisee_settings: dict, service_configuration_name: str, service_configuration_id: str, run_as_user: str, 
                schema: str, table_name_format: str, only_entity_names: list) -> None:
        self.profisee_settings = profisee_settings
        self.service_configuration_name = service_configuration_name
        self.service_configuration_id = service_configuration_id
        self.run_as_user = run_as_user
        self.schema = schema
        self.table_name_format = table_name_format
        self.only_entity_names = only_entity_names

    def generate(self) -> None:
        print(f"Connecting to '{self.profisee_settings["ProfiseeUrl"]}'")
        logger.info(f"Connecting to '{self.profisee_settings["ProfiseeUrl"]}'")
        api = Restful.API(self.profisee_settings["ProfiseeUrl"], self.profisee_settings["ClientId"], verify = self.profisee_settings.get("VerifySSL", True))

        entities = api.GetEntities()

        for entity in entities:
            entity_name = entity["identifier"]["name"]
            entity_id = entity["identifier"]["id"]

            table_name = self.table_name_format.format(entity_name=entity_name)

            if not self.only_entity_names or entity_name.lower() in map(str.lower, self.only_entity_names):

                export_parameters = {}
                import_parameters = {}
                
                attributes = api.GetAttributes(entity_name)       
                for attribute in sorted(attributes, key = lambda attribute : attribute["sortOrder"]):
                    
                    attribute_name = attribute["identifier"]["name"]
                    attribute_id = attribute["identifier"]["id"]

                    export_parameters[attribute_name] = {
                            "name": attribute_name,
                            "assignmentType": "Expression",
                            "value": {
                                "name": attribute_name,
                                "expressionText": f"[{entity_name}].[{attribute_name}|{attribute_id}]"
                            },
                            "dataType": 1
                        }
                    
                    import_parameters[f"[{entity_name}].[{attribute_name}|{attribute_id}]"] = {
                        "assignmentType": "Expression",
                        "value": {
                            "name": attribute_name,
                            "expressionText": f"[{table_name}].[{attribute_name}]"
                        },
                        "dataType": 1
                    }

                export_strategy = {
                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyArtifact, Profisee.Platform.ConnEx",
                    "artifactVersion": "1.3.1.0",
                    "integrationStrategyRecord": { 
                        "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyConfigurationRecord, Profisee.Platform.ConnEx",
                        "Configuration": {
                            "$type": "Profisee.Platform.ConnEx.Contracts.Administration.DatabaseIntegrationStrategyConfiguration, Profisee.Platform.ConnEx",
                            "entityId": {
                                "$type": "Profisee.Platform.Cdp.Contracts.Identifier, Profisee.Platform.Cdp",
                                "id": entity_id,
                                "name": entity_name
                            },
                            "serviceConfigurationId": {
                                "$type": "Profisee.Platform.Cdp.Contracts.Identifier, Profisee.Platform.Cdp",
                                "id": self.service_configuration_id,
                                "name": self.service_configuration_name
                            },
                            "integrationFlow": "Export",
                            "databaseType": "SqlServer",
                            "remoteObjectType": "Table",
                            "remoteSchema": "dbo",
                            "remoteObjectName": table_name,
                            "mappings": {
                                "$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                                table_name: {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx",
                                    "name": table_name,
                                    "assignmentType": "ArrayExpression",
                                    "value": {
                                        "dataSource": f"{entity_name}|{entity_id}",
                                        "parameters": export_parameters                        
                                    },
                                    "dataType": 2
                                }
                            },
                            "runAsUser": self.run_as_user,
                            "maximumRecordsPerJob": 1000,
                            "triggeringRules": {
                                "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyTriggeringRuleCollection, Profisee.Platform.ConnEx",
                                "onDemandExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.OnDemandExecutionOptions, Profisee.Platform.ConnEx",
                                    "allowSynchronousExecution": False,
                                    "allowAsynchronousExecution": True,
                                    "maxRecordsPerSynchronousExecution": 1
                                },
                                "continuousExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ContinuousExecutionOptions, Profisee.Platform.ConnEx",
                                    "shouldTriggerOnRecordsAdded": True,
                                    "shouldTriggerOnRecordsUpdated": True,
                                    "shouldTriggerOnRecordsDeleted": False,
                                    "shouldDeleteRecordsInTarget": False
                                },
                                "scheduledExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ScheduledExecutionOptions, Profisee.Platform.ConnEx",
                                    "schedules": {
                                        "$type": "System.Collections.Generic.List`1[[Profisee.Platform.ConnEx.Contracts.Administration.IntegrationSchedule, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                                        "$values": []
                                    }
                                }
                            },
                            "artifactVersion": "1.3.1.0"                
                        },
                        "Id": str(uuid.uuid4()),
                        "Name": f"SQL Server [{entity_name}] Export [{self.schema}].[{table_name}]",
                        "Type": "Database"
                    }    
                }

                with open(f"SQL Server [{entity_name}] Export [{self.schema}].[{table_name}].json", 'w') as file :
                    file.write(json.dumps(export_strategy, indent=4))
                    
                import_strategy = {
                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyArtifact, Profisee.Platform.ConnEx",
                    "artifactVersion": "1.3.1.0",
                    "integrationStrategyRecord": {
                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyConfigurationRecord, Profisee.Platform.ConnEx",
                        "Configuration": {
                            "$type": "Profisee.Platform.ConnEx.Contracts.Administration.DatabaseIntegrationStrategyConfiguration, Profisee.Platform.ConnEx",
                            "entityId": {
                                "$type": "Profisee.Platform.Cdp.Contracts.Identifier, Profisee.Platform.Cdp",
                                "id": entity_id,
                                "name": entity_name
                            },
                            "serviceConfigurationId": {
                                "$type": "Profisee.Platform.Cdp.Contracts.Identifier, Profisee.Platform.Cdp",
                                "id": self.service_configuration_id,
                                "name": self.service_configuration_name
                            },
                            "integrationFlow": "Import",
                            "databaseType": "SqlServer",
                            "remoteObjectType": "Table",
                            "remoteSchema": "dbo",
                            "remoteObjectName": table_name,
                            "mappings": {
                                "$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                                f"{entity_name}|{entity_id}": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx",
                                    "name": entity_name,
                                    "assignmentType": "ArrayExpression",
                                    "value": {
                                        "dataSource": table_name,
                                        "parameters": import_parameters
                                    },
                                    "dataType": 2
                                }
                            },
                            "runAsUser": self.run_as_user,
                            "maximumRecordsPerJob": 1000,
                            "triggeringRules": {
                                "$type": "Profisee.Platform.ConnEx.Contracts.Administration.IntegrationStrategyTriggeringRuleCollection, Profisee.Platform.ConnEx",
                                "onDemandExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.OnDemandExecutionOptions, Profisee.Platform.ConnEx",
                                    "allowSynchronousExecution": False,
                                    "allowAsynchronousExecution": True,
                                    "maxRecordsPerSynchronousExecution": 1
                                },
                                "continuousExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ContinuousExecutionOptions, Profisee.Platform.ConnEx",
                                    "shouldTriggerOnRecordsAdded": False,
                                    "shouldTriggerOnRecordsUpdated": False,
                                    "shouldTriggerOnRecordsDeleted": False,
                                    "shouldDeleteRecordsInTarget": False
                                },
                                "scheduledExecution": {
                                    "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ScheduledExecutionOptions, Profisee.Platform.ConnEx",
                                    "schedules": {
                                        "$type": "System.Collections.Generic.List`1[[Profisee.Platform.ConnEx.Contracts.Administration.IntegrationSchedule, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                                        "$values": []
                                    }
                                }
                            },
                            "artifactVersion": "1.3.1.0"
                        },
                        "Id": str(uuid.uuid4()),
                        "Name": f"SQL Server [{self.schema}].[{table_name}] Import [{entity_name}]",
                        "Type": "Database"
                    }
                }

                with open(f"SQL Server [{self.schema}].[{table_name}] Import [{entity_name}].json", 'w') as file :
                    file.write(json.dumps(import_strategy, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SQL Connect Import and Export Strategies.")
    parser.add_argument("--instance", type=str, default="Local", help="The instance name to use from settings.json")
    parser.add_argument("--service_configuration_name", type=str, default="SQL Server Configuration - Local", help="The service configuration name.")
    parser.add_argument("--service_configuration_id", type=str, default="9c8449a1-be87-4644-a62d-d3c1f87c5b6d", help="The service configuration ID.")
    parser.add_argument("--run_as_user", type=str, default="corp\\detlefgr", help="The user to run the integration as")
    parser.add_argument("--schema_name", type=str, default="dbo", help="The schema to use for table names")
    parser.add_argument("--table_name_format", type=str, default="tbl_{entity_name}", help="The format for table names")
    parser.add_argument("--only_entity_names", type=str, nargs='*', default=["test"], help="List of entity names to include (if empty, all entities are included)")

    args = parser.parse_args()
    
    instance_name = args.instance
    service_configuration_name = args.service_configuration_name
    service_configuration_id = args.service_configuration_id
    run_as_user = args.run_as_user
    schema_name = args.schema_name
    table_name_format = args.table_name_format
    only_entity_names = args.only_entity_names
    
    logger.info(f"Using instance '{instance_name}'")
    logger.info(f"Using service_configuration_name '{service_configuration_name}'")
    logger.info(f"Using service_configuration_id '{service_configuration_id}'")
    logger.info(f"Using run_as_user '{run_as_user}'")
    logger.info(f"Using schema_name '{schema_name}'")
    logger.info(f"Using table_name_format '{table_name_format}'")
    logger.info(f"Using only_entity_names '{only_entity_names}'")
        
    with open('settings.json', 'r') as file: settings = json.load(file)
    profisee_settings = settings[instance_name]
    
    logger.info(f"Settings for instance '{instance_name}': {profisee_settings}")
        
    connect_generate_connect_strategy = ConnectGeneratorConnectStrategy(profisee_settings, 
                                                                        service_configuration_name, 
                                                                        service_configuration_id, 
                                                                        run_as_user,
                                                                        schema_name,
                                                                        table_name_format,
                                                                        only_entity_names)
    connect_generate_connect_strategy.generate()