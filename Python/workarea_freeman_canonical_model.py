import os, json

from Profisee.Restful import API, Entity, Attribute
from Profisee.Common import Common
from Profisee.Restful.Enums import AttributeType, AttributeDataType


if os.path.exists(r"settings.json"):
    settings = json.load(open(r"settings.json"))
elif os.path.exists(r"Python/settings.json"):
    settings = json.load(open(r"Python/settings.json"))
elif os.path.exists(r"_Internal/settings.json"):
    settings = json.load(open(r"_Internal/settings.json"))
else:
    print("You must provide a settings.json file with the ProfiseeUrl, ClientId.")
    exit(1)

profisee_url = Common.Get(settings, "ProfiseeUrl", None)
client_id = Common.Get(settings, "ClientId", None)
verify_ssl = Common.Get(settings, "VerifySSL", True)

api = API(profisee_url, client_id, verify_ssl)


def create_entity(entity_name: str, attribute_list: list) -> None:
    api.CreateEntity(Entity(entity_name).to_Entity())
    print(f"Created entity '{entity_name}' StatusCode={api.StatusCode}")
    
    attributes = []
    for attribute in attribute_list:
        attribute.EntityName = entity_name
        attributes.append(attribute.to_Attribute())
    if len(attributes):
        api.CreateAttributes(attributes)
        print(f"  Created {len(attributes)} attributes for entity '{entity_name}' StatusCode={api.StatusCode}")

description_attribute_list = [ Attribute(None, "Description", AttributeType.FreeForm, AttributeDataType.Text, 500) ]

create_entity("FM_RegionRef", description_attribute_list)
create_entity("FM_BargainingUnitRef", description_attribute_list)
create_entity("FM_SpecialAgreementRef", description_attribute_list)
create_entity("FM_WorkerTypeRef", description_attribute_list)
create_entity("FM_EmploymentStatusRef", description_attribute_list)

create_entity("FM_UnionRef", [ Attribute(None, "UnionName", AttributeType.FreeForm, AttributeDataType.Text, 100) ])

create_entity("FM_JobCodeRef", [     
    Attribute(None, "JobTitle", AttributeType.FreeForm, AttributeDataType.Text, 200),
    Attribute(None, "JobFamily", AttributeType.FreeForm, AttributeDataType.Text, 400),
    Attribute(None, "FLSAStatus", AttributeType.FreeForm, AttributeDataType.Text, 100)
])

create_entity("FM_EmployeeGroupRef", [ Attribute(None, "EmployeeGroupName", AttributeType.FreeForm, AttributeDataType.Text, 100) ])
create_entity("FM_OrgUnitRef", [ Attribute(None, "OrgUnitName", AttributeType.FreeForm, AttributeDataType.Text, 100) ])

create_entity("FM_LegalEntityRef", [     
    Attribute(None, "EntityName", AttributeType.FreeForm, AttributeDataType.Text, 200),
    Attribute(None, "Country", AttributeType.FreeForm, AttributeDataType.Text, 400),
    Attribute(None, "Region", AttributeType.FreeForm, AttributeDataType.Text, 100)
])

create_entity("FM_Core_YesNo", [])

create_entity("FM_Person", [     
    Attribute(None, "FirstName", AttributeType.FreeForm, AttributeDataType.Text, 200),
    Attribute(None, "LastName", AttributeType.FreeForm, AttributeDataType.Text, 400),
    Attribute(None, "PreferredName", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "EmailAddress", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "PhoneNumber", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "WorkerTypeCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_WorkerTypeRef"),
    Attribute(None, "EmploymentStatusCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_EmploymentStatusRef"),
    Attribute(None, "StartDate", AttributeType.FreeForm, AttributeDataType.Date),
    Attribute(None, "EndDate", AttributeType.FreeForm, AttributeDataType.Date)
])

create_entity("FM_Classification", [     
    Attribute(None, "PersonId", AttributeType.Domain, AttributeDataType.Text, domain="FM_Person"),
    Attribute(None, "IncludedInHeadcount", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "PaidThroughPayroll", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "AccessClassification", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "ProvisioningGroup", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "RegionCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_RegionRef"),
    Attribute(None, "ContractorFlag", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "ConsentRequired", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "UnionFlag", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "UnionCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_UnionRef"),
    Attribute(None, "BargainingUnitCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_BargainingUnitRef"),
    Attribute(None, "SpecialAgreementCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_SpecialAgreementRef"),
    Attribute(None, "IsServiceProvider", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo")
])

create_entity("FM_Assignment", [     
    Attribute(None, "PersonId", AttributeType.Domain, AttributeDataType.Text, domain="FM_Person"),
    Attribute(None, "JobCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_JobCodeRef"),
    Attribute(None, "AssignmentTitle", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "EmployeeGroup", AttributeType.Domain, AttributeDataType.Text, domain="FM_EmployeeGroupRef"),
    Attribute(None, "OrgUnitCode", AttributeType.Domain, AttributeDataType.Text, domain="FM_OrgUnitRef"),
    Attribute(None, "Location", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "ManagerId", AttributeType.Domain, AttributeDataType.Text, domain="FM_Assignment"),
    Attribute(None, "CostCenter", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "LegalEntityId", AttributeType.Domain, AttributeDataType.Text, domain="FM_LegalEntityRef"),
    Attribute(None, "EffectiveStartDate", AttributeType.FreeForm, AttributeDataType.Date),
    Attribute(None, "EffectiveEndDate", AttributeType.FreeForm, AttributeDataType.Date),
    Attribute(None, "IsCurrentAssignment", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "ReasonCode", AttributeType.FreeForm, AttributeDataType.Text, 100),
    Attribute(None, "IncludedInHeadcount", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
    Attribute(None, "PaidThroughPayroll", AttributeType.Domain, AttributeDataType.Text, domain="FM_Core_YesNo"),
])
