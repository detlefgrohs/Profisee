import json
from ConnectGeneratorSQLDDL import ConnectGeneratorSQLDDL
from ConnectGeneratorConnectStrategy import ConnectGeneratorConnectStrategy

instance_name = "Local"
profisee_settings = json.load(open(r"settings.json"))[instance_name]




service_configuration_name = "SQL Server Configuration - Local"
service_configuration_id = "9c8449a1-be87-4644-a62d-d3c1f87c5b6d"

run_as_user = "corp\\detlefgr"
schema_name = "dbo"
table_name_format = "tbl_{entity_name}"
only_entity_names = [ "DQParent", "DQChild" ]
maximum_records_per_batch = 50000

    """
    
    This will generate a specification like the format below that will be used to create a Connect Strategy.
    
    This will allow for finer control of the Connect Strategy than the current implementation in ConnectGeneratorConnectStrategy.py
    
    """

spec = {
    "ServiceConfigurationName": service_configuration_name,
    "ServiceConfigurationId": service_configuration_id,
    "RunAsUser": run_as_user,
    "MaximumRecordsPerBatch": maximum_records_per_batch,
    
    "Entities": {
        "DQParent": {
            "IncludeInMapping": True,
            "SchemaName": "dbo",
            "TableName": "tbl_DQParent",
            "AttributeMappings": {
                "Name" : {"FieldName": "Name", "IncludeInMapping": True},
                "Code" : {"FieldName": "Code", "IncludeInMapping": True}
            }
        },
        "DQChild": {
            "IncludeInMapping": True,
            "SchemaName": "dbo",
            "TableName": "tbl_DQChild",
            "AttributeMappings": {
                "Name" : {"FieldName": "Name", "IncludeInMapping": True},
                "Code" : {"FieldName": "Code", "IncludeInMapping": True}
            }
        }
    }
}

# ConnectGeneratorSQLDDL(profisee_settings, schema_name, table_name_format, only_entity_names).generate()

#ConnectGeneratorConnectStrategy(profisee_settings, service_configuration_name, service_configuration_id, run_as_user,
#                                schema_name, table_name_format, only_entity_names).generate()
