import logging, json, os, uuid
from Profisee import Restful

instance_name = "Local"

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info(f"Running {__file__}")

with open('settings.json', 'r') as file: 
    settings = json.load(file)
profisee_settings = settings[instance_name]

print(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
logger.info(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
api = Restful.API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify = False)

service_configuration_name = "SQL Server Configuration - Local"
service_configuration_id = "9c8449a1-be87-4644-a62d-d3c1f87c5b6d"
run_as_user = "corp\\detlefgr"

entities = api.GetEntities()
only_entity_names = [ "Test" ]

for entity in entities:
    entity_name = entity["identifier"]["name"]
    entity_id = entity["identifier"]["id"]

    if not only_entity_names or entity_name in only_entity_names:

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
                    "expressionText": f"[tbl_{entity_name}].[{attribute_name}]"
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
                        "id": service_configuration_id,
                        "name": service_configuration_name
                    },
                    "integrationFlow": "Export",
                    "databaseType": "SqlServer",
                    "remoteObjectType": "Table",
                    "remoteSchema": "dbo",
                    "remoteObjectName": f"tbl_{entity_name}",
                    "mappings": {
                        "$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                        f"tbl_{entity_name}": {
                            "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx",
                            "name": f"tbl_{entity_name}",
                            "assignmentType": "ArrayExpression",
                            "value": {
                                "dataSource": f"{entity_name}|{entity_id}",
                                "parameters": export_parameters                        
                            },
                            "dataType": 2
                        }
                    },
                    "runAsUser": run_as_user,
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
                "Name": f"SQL Server [{entity_name}] Export [dbo].[tbl_{entity_name}]",
                "Type": "Database"
            }    
        }

        with open(f"SQL Server [{entity_name}] Export [dbo].[tbl_{entity_name}].json", 'w') as file :
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
                        "id": service_configuration_id,
                        "name": service_configuration_name
                    },
                    "integrationFlow": "Import",
                    "databaseType": "SqlServer",
                    "remoteObjectType": "Table",
                    "remoteSchema": "dbo",
                    "remoteObjectName": f"tbl_{entity_name}",
                    "mappings": {
                        "$type": "System.Collections.Generic.Dictionary`2[[System.String, System.Private.CoreLib],[Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx]], System.Private.CoreLib",
                        f"{entity_name}|{entity_id}": {
                            "$type": "Profisee.Platform.ConnEx.Contracts.Administration.ParameterAssignmentConfiguration, Profisee.Platform.ConnEx",
                            "name": entity_name,
                            "assignmentType": "ArrayExpression",
                            "value": {
                                "dataSource": f"tbl_{entity_name}",
                                "parameters": import_parameters
                            },
                            "dataType": 2
                        }
                    },
                    "runAsUser": run_as_user,
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
                "Name": f"SQL Server [dbo].[tbl_{entity_name}] Import [{entity_name}]",
                "Type": "Database"
            }
        }
        
        with open(f"SQL Server [dbo].[tbl_{entity_name}] Import [{entity_name}].json", 'w') as file :
            file.write(json.dumps(import_strategy, indent=4))
        
        
