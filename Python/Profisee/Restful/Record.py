from typing import Final
from Profisee.Common import Common

class Record :
    EXCLUDED_ATTRIBUTES : Final = [
        "ID", 
        "InternalID",
        "$RecordAvatar",
        "EnterUserName",
        "EnterDTM",
        "LastChgUserName",
        "LastChgDTM",
        "$LastChgDataTransactionID",
        "$LastChgTypeID",
        "CanUpdate",
        "CanDelete"
    ]
    
    def __init__(self, code = None, name = None, record = None) :
        if record != None : 
            self.Record = record
        else :
            self.Record = {
                "Name" : name,
                "Code" : code
            }
        
    @property
    def Code(self) : return self.Get("Code")
    
    @Code.setter
    def Code(self, value) : self.Set("Code", value)

    @property
    def Name(self) : return self.Get("Name")
    
    @Name.setter
    def Name(self, value) : self.Set("Name", value)
        
    @classmethod
    def from_Object(cls, record) :  
        return cls(record = record)
        
    def Set(self, attributeName, value) :
        Common.Set(self.Record, attributeName, value)
        
    def Get(self, attributeName) :
        return Common.Get(self.Record, attributeName)     
  