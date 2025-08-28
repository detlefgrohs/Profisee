from Profisee.Common import Common, null_guid

class Entity :
    def __init__(self, name) :
        self.ID = null_guid
        self.Name = name
        self.LongDescription = ""
        self.IconName = None
        self.IsCodeGenerationEnabled = False
        self.CodeGenerationSeed = 0
        self.FileCategories = None
        
    @classmethod
    def from_Entity(cls, entity) :
        return cls("").Load(entity)
        
    def to_Entity(self) :
        return {
            "Identifier" : {
                "ID" : str(self.ID),
                "Name" : self.Name
            },
            "LongDescription" : self.LongDescription,
            "IconName" : self.LongDescription,
            "IsCodeGenerationEnabled" : self.IsCodeGenerationEnabled,
            "CodeGenerationSeed" : self.CodeGenerationSeed,
            "FileCategories" : self.FileCategories
        }
        
    def Load(self, entity) :
        self.ID = Common.Get(Common.Get(entity, "Identifier"), "ID")
        if self.ID == None : self.ID = str(null_guid)
        self.Name = Common.Get(Common.Get(entity, "Identifier"), "Name")
        self.LongDescription = Common.Get(entity, "LongDescription")
        return self