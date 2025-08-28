from Profisee.Restful.Enums import DbaFormatEnum

class GetOptions :
    def __init__(self, filter="") :
        self.Filter = filter
        self.OrderBy = ""
        self.Attributes = []
        self.DbaFormat = DbaFormatEnum.Default
        self.CountsOnly = False
        self.PageNumber = 1
        self.PageSize = 50 
        
    def __repr__(self) :
        return self.QueryString()
        
    def __str__(self) :
        return self.QueryString()
        
    def QueryString(self):
        queryStringList = []
        if (self.Filter != ""): queryStringList.append(f"Filter={self.Filter}")        
        if (self.PageNumber != 1): queryStringList.append(f"PageNumber={str(self.PageNumber)}")
        if (self.PageSize != 50): queryStringList.append(f"PageSize={str(self.PageSize)}")
        if (self.OrderBy != ""): queryStringList.append(f"OrderBy={self.OrderBy}")
        if (len(self.Attributes) > 0): queryStringList.append(f"Attributes=" + ",".join(self.Attributes))
        if (self.DbaFormat != DbaFormatEnum.Default): queryStringList.append(f"DbaFormat={str(self.DbaFormat.value)}")
        if (self.CountsOnly): queryStringList.append(f"CountsOnly=true")
            
        return "&".join(queryStringList)