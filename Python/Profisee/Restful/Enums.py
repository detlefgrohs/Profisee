from enum import Enum

class DbaFormatEnum(Enum) :
    Default = 0
    CodeOnly = 1
    CodeAndName = 2

class AttributeDataType(Enum) :
    NotSpecified = 0
    Text = 1
    Number = 2
    DateTime = 3
    Date = 4
    Link = 6
    
class AttributeType(Enum) :
    NotSpecified = 0
    FreeForm = 1
    Domain = 2
    System = 3
    File = 4
    
class ProcessActions(Enum) :
    MatchingOnly = 0
    MatchingAndSurvivorship = 1
    SurvivorshipOnly = 2
    ClearPriorResults = 3
    ClearAllPriorResults = 4
    
class MatchingStatus(Enum) :
    Disabled = 0
    Enabled = 1
    EnabledWithClustering = 2
    EnabledWithClusteringAndSurvivorship = 3
    EnabledWithSurvivorship = 4
    
class RequestOperation(Enum) :
    Get = 0
    Put = 1
    Post = 2
    Patch = 3
    Delete = 4
    
class WorkflowInstanceStatus(Enum) :
    All = -1
    Undefined = 0
    Completed = 1
    Suspended = 2
    Running = 3
