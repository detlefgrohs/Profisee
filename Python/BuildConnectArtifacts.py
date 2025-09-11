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
only_entity_names = ["Test"]

ConnectGeneratorSQLDDL(profisee_settings, schema_name, table_name_format, only_entity_names).generate()

ConnectGeneratorConnectStrategy(profisee_settings, service_configuration_name, service_configuration_id, run_as_user,
                                schema_name, table_name_format, only_entity_names).generate()
