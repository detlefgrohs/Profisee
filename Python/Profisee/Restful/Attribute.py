from Profisee.Restful.Enums import AttributeType, AttributeDataType
from Profisee.Common import null_guid

class Attribute :
    def __init__(self, entityName, name, attributeType : AttributeType = AttributeType.FreeForm, dataType : AttributeDataType = AttributeDataType.Text, length = 200) :
        self.EntityName = entityName
        self.Name = name
        self.AttributeType = attributeType
        self.DataType = dataType
        self.Length = length
        self.Domain = None

    @classmethod
    def from_Attribute(cls, attribute) :
        return cls("", "").Load(attribute)        
        
    def to_Attribute(self) :
        payload = {
            "Identifier" : {
                "Name" : self.Name,
                "EntityId" : {
                    "Name" : self.EntityName
                }
            },
            "AttributeType": self.AttributeType.value,
            "DataType": self.DataType.value,
            "DataTypeInformation": self.Length
        }
        
        if self.Domain != None :
            payload["DomainEntityId"] = {
                "Name" : self.Domain,
                "Id" : str(null_guid)
            }
        
        return payload
        
    def Load(self, attribute) :
        # self.ID = Common.Get(Common.Get(entity, "Identifier"), "ID")
        # if self.ID == None : self.ID = str(null_guid)
        # self.Name = Common.Get(Common.Get(entity, "Identifier"), "Name")
        # self.LongDescription = Common.Get(entity, "LongDescription")
        return self