import requests, inspect, logging
import urllib3
from urllib.parse import urljoin
from typing import Any, Dict

from Profisee.Restful.GetOptions import GetOptions
from Profisee.Common import Common
from Profisee.Restful.Enums import ProcessActions, MatchingStatus, RequestOperation, WorkflowInstanceStatus

class API() :
    """Class to handle requests and responses from the Profisee Restful API.
    """
    def __init__(self, profisee_url, client_id, verify_ssl = True) -> None:
        """Constructor for Restful API. Sets connection and response handlers.

        Args:
            profiseeUrl (string): URL to Profisee instance.
            clientId (string): Client ID to access Profisee instance.
        """
        self.ProfiseeUrl = profisee_url
        self.ClientId = client_id
        self.SetResponseHandlers()
        self.VerifySSL = verify_ssl
        self.LastResponse = None
        self.StatusCode = None
        
        if self.VerifySSL == False : urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if not self.ProfiseeUrl.endswith("/") : self.ProfiseeUrl += "/" # Ensure that the URL ends with a /
                
    def IsSuccessStatusCode(self) -> bool :
        return self.StatusCode >= 200 and self.StatusCode < 300
        
    def SetResponseHandlers(self) :
        """Creates the ResponseHandlers that is used to handle the responses for the different status_codes."""
        self.ResponseHandlers = {
            ("UnmatchRecords", 204) : lambda response : self.SuccessHandler(response, "Success - records unmatched"),
            ("UpdateMatchingStrategy", 204) : lambda response : self.SuccessHandler(response, "Success - Successfully updated the continuous matching setting of the matching strategy."),

            (None, 200) : lambda response : self.SuccessDataHandler(response),
            (None, 201) : lambda response : self.SuccessDataHandler(response),
            (None, 207) : lambda response : self.SuccessDataHandler(response), # Success with some errors....
            
            (None, 400) : lambda response : self.ErrorHandler(response, "Bad Request - One or more validation errors occurred."),
            (None, 401) : lambda response : self.ErrorHandler(response, "Not Authorized - You are not authorized to access this resource."),
            (None, 404) : lambda response : self.ErrorHandler(response, "Not Found - The requested entity could not be found."),
            (None, 500) : lambda response : self.ErrorHandler(response, "Internal Server Error - An unexpected error occurred on the server. Please check your Profisee logs for more details.")
        }
        
    def GetHeaders(self) :
        """Returns the headers for all requests.
        
        Returns:
            dictionary : Header objects to be used in the requests.
        """
        return {
            "Content-Type" : "application/json",
            "x-api-key" : self.ClientId
        }
        
    def CheckResponse(self, response) -> Any:
        """Checks response against ResponseHandlers and creates modified response as needed.

        Args:
            response (dictionary) : response dictionary from requests.

        Returns:
            dictionary : modified response object based on ResponseHandler.
        """
        logging.getLogger().debug(f"response : statusCode = {response.status_code} text = '{response.text}'")
        self.LastResponse = response
        self.StatusCode = response.status_code
        caller_name = inspect.stack()[1].function
        
        if (caller_name, response.status_code) in self.ResponseHandlers :
            returnValue = self.ResponseHandlers[(caller_name, response.status_code)](response)
        elif (None, response.status_code) in self.ResponseHandlers :
            returnValue = self.ResponseHandlers[(None, response.status_code)](response)
        else :
            returnValue = {
                "Error" : f"Unknown statusCode '{response.status_code}'"
            }
        logging.getLogger().debug(f"returnValue = '{returnValue}'")
        return returnValue

    # Response Handlers
    def SuccessHandler(self, response: dict[str, Any], message: str) -> dict[str, Any]:
        """Handle success response that does not have data.

        Args:
            response (dictionary): response dictionary from requests
            message (string): message to include in modified response

        Returns:
            dictionary: modified response with status code and message.
        """
        self.errors = None
        return { 
            "StatusCode" : response.status_code,
            "Message" : message
        }

    def SuccessDataHandler(self, response: dict[str, Any]) -> dict[str, Any]:
        """Handle success response that returns data from original response

        Args:
            response (dictionary): response dictionary from requests

        Returns:
            dictionary: modified response with the data from original response
        """
        json = self.LastResponse.json()
        self.errors = Common.Get(json, "errors", None)
        return json['data'] if Common.Get(json, "data") != None else json

    def ErrorHandler(self, response: dict[str, Any], message: str) -> dict[str, Any]:
        """_summary_

        Args:
            response (dictionary): response dictionary from requests
            message (string): message to include in modified response

        Returns:
            dictionary: modified response with status code, message and original error from response
        """
        self.errors = { response.status_code : response.text }
        return { 
            "StatusCode" : response.status_code,
            "Message" : message,
            "Error" : response.text
        }
        
    @Common.LogFunction
    def CallAPI(self, requestOperation : RequestOperation, url: str, json: dict[str, Any] = None) -> dict[str, Any]:
        """_summary_

        Args:
            requestOperation (RequestOperation): _description_
            url (_type_): _description_
            json (_type_, optional): _description_. Defaults to None.

        Returns:
            dictionary : modified response object based on call to CheckResponse().
        """
        url = urljoin(self.ProfiseeUrl, url)
        match requestOperation :
            case RequestOperation.Get :
                return self.CheckResponse(requests.get(url, json = json, headers = self.GetHeaders(), verify = self.VerifySSL))
            case RequestOperation.Put :
                return self.CheckResponse(requests.put(url, json = json, headers = self.GetHeaders(), verify = self.VerifySSL))
            case RequestOperation.Post :
                return self.CheckResponse(requests.post(url, json = json, headers = self.GetHeaders(), verify = self.VerifySSL)) 
            case RequestOperation.Patch :
                return self.CheckResponse(requests.patch(url, json = json, headers = self.GetHeaders(), verify = self.VerifySSL))
            case RequestOperation.Delete :
                return self.CheckResponse(requests.delete(url, json = json, headers = self.GetHeaders(), verify = self.VerifySSL))

# Helper Methods
    def ChangeAttributeName(self, entityName, oldAttributeName, newAttributeName) :
        attribute = self.GetAttribute(entityName, oldAttributeName)
        if self.StatusCode != 404 :
            attribute['identifier']['name'] = newAttributeName
            self.UpdateAttribute(attribute)


#############################################################################
# AddressVerification
#############################################################################    @Common.LogFunction
    @Common.LogFunction
    def GetAddressVerificationStrategies(self) -> list[dict[str, Any]]:
        return self.CallAPI(RequestOperation.Get, "rest/v1/AddressVerificationStrategies")
    @Common.LogFunction
    def GetAddressVerificationStrategy(self, strategyName) -> dict[str, Any]:
        return self.CallAPI(RequestOperation.Get, f"rest/v1/AddressVerificationStrategies/{strategyName}")
    @Common.LogFunction
    def GetAddressVerificationStrategyAttributes(self, strategyName, recordCode) :
        return self.CallAPI(RequestOperation.Get, f"rest/v1/AddressVerificationStrategies/{strategyName}/address?recordCode={recordCode}")
    @Common.LogFunction
    def StartAddressVerificationStrategy(self, strategyName, body) :
        return self.CallAPI(RequestOperation.Post, f"rest/v1/AddressVerificationStrategies/{strategyName}/job", json = body)
    @Common.LogFunction
    def StartAddressVerificationStrategy(self, strategyName, records) :
        return self.CallAPI(RequestOperation.Post, f"rest/v1/AddressVerificationStrategies/{strategyName}/records", json = records)
    @Common.LogFunction
    def StopAddressVerificationStrategy(self, strategyName) :
        return self.CallAPI(RequestOperation.Put, f"rest/v1/AddressVerificationStrategies/{strategyName}/job/cancel")

#############################################################################        
# Attributes
#############################################################################    @Common.LogFunction
    @Common.LogFunction
    def GetAttributes(self, entity_name: str = None) -> Dict[str, Any]:
        if entity_name is None :
            return self.CallAPI(RequestOperation.Get, "rest/v1/Attributes")
        else :
            return self.CallAPI(RequestOperation.Get, f"rest/v1/Entities/{entity_name}/attributes")
    @Common.LogFunction       
    def GetAttribute(self, entity_name:str, attribute_name:str) -> Dict[str, Any]:
        return self.CallAPI(RequestOperation.Get, f"rest/v1/Entities/{entity_name}/attributes/{attribute_name}")
    @Common.LogFunction
    def CreateAttribute(self, attribute: Dict[str, Any]) -> Dict[str, Any]:
        """_summary_

        Args:
            attribute (dictionary): Attribute to be created

        Returns:
            dictionary: Attribute creation information
        """
        return self.CallAPI(RequestOperation.Post, "rest/v1/Attributes", json = [attribute])

    @Common.LogFunction
    def CreateAttributes(self, attributes: list[Dict[str, Any]]) -> Dict[str, Any]:
        """_summary_

        Args:
            attributes (list): Attributes to be created

        Returns:
            dictionary: Attribute creation information
        """
        # self.CallAPI(RequestOperation.Post, "rest/v1/Attributes", json = attributes)
        for attribute in attributes:
            self.CreateAttribute(attribute)

    @Common.LogFunction
    def UpdateAttribute(self, attribute) :
        self.UpdateAttributes([ attribute ])
        
    @Common.LogFunction
    def UpdateAttributes(self, attributes) :
        return self.CallAPI(RequestOperation.Put, "rest/v1/Attributes", json = attributes)

    @Common.LogFunction
    def DeleteAttributes(self, attributeNames) :
        raise NotImplementedError("DeleteAttributes not implemented yet...")
    # DELETE  DeleteAttributes(entityName, attributeNames[])
    
    @Common.LogFunction
    def DeleteAttribute(self, attributeName) :
        raise NotImplementedError("DeleteAttribute not implemented yet...")    
    # DELETE  DeleteAttribute(entityName, attributeName)      

#############################################################################
# Auth
#############################################################################
    def GetAuthenticationURL(self) :
        return self.CallAPI(RequestOperation.Get, "rest/v1/Auth")

#############################################################################
## Connect
#############################################################################
    def RunConnectBatch(self, strategy_name, filter = None, record_codes = None) :
        body = {
            "FilterExpression" : filter if filter is not None else "",
            "Codes" : record_codes if record_codes is not None else [ ]
        }
        return self.CallAPI(RequestOperation.Post, f"rest/v1/Connect/Strategies/{strategy_name}/Batch", json = body)

    def RunConnectImmediate(self, strategy_name:str, record_codes: list[str]) -> dict[str, Any]:
        return self.CallAPI(RequestOperation.Post, f"rest/v1/Connect/Strategies/{strategy_name}/Immediate", json = record_codes)

    # Come back to this one...

#############################################################################
## DataQualityIssues
#############################################################################
    def GetDataQualityIssues(self, entityName:str, record_codes: list[str], getOptions: GetOptions) -> dict[str, Any]:
        pass
        # return self.CallAPI(RequestOperation.Get, f"rest/v1/DataQualityIssues/{entityName}", params=getOptions)

#############################################################################
## DataQualityRules
#############################################################################
    def GetDataQualityRules(self, entityName: str) -> dict[str, Any]:
        pass
        # return self.CallAPI(RequestOperation.Get, f"rest/v1/DataQualityRules/{entityName}")

    def GetDataQualityRule(self, dataQualityRuleName: str) -> dict[str, Any]:
        pass
        # return self.CallAPI(RequestOperation.Get, f"rest/v1/DataQualityRules/{dataQualityRuleName}")

    def GetDataQualityOperatorTypes(self) -> dict[str, Any]:
        pass
        # return self.CallAPI(RequestOperation.Get, "rest/v1/DataQualityRules/operatorTypes")

#############################################################################
## Entities
#############################################################################
    @Common.LogFunction
    def GetEntities(self) -> dict[str, Any]:
        """Returns all entities from Profisee instance.

        Returns:
            dictionary: List of entities from Profisee instance.
        """
        return self.CallAPI(RequestOperation.Get, "rest/v1/Entities")

    def GetEntity(self, entityName) :
        return self.CallAPI(RequestOperation.Get, f"rest/v1/Entities/{entityName}")

    def CreateEntity(self, entity) :
        self.CallAPI(RequestOperation.Post, "rest/v1/Entities", json = [entity])
    
    def UpdateEntity(self, entity) :
        raise NotImplementedError("UpdateEntity not implemented yet...")    
    # PUT     UpdateEntity(entityObject)

    def DeleteEntities(self, entityNames) :
        raise NotImplementedError("DeleteEntities not implemented yet...")    
    # DELETE  DeleteEntities(entityNames[])
    
    @Common.LogFunction
    def DeleteEntity(self, entityName:str) -> dict[str, Any]:
        """_summary_

        Args:
            entityName (string): Name of entity to delete from instance.

        Returns:
            dictionary: deletion information.
        """
        return self.CallAPI(RequestOperation.Delete, f"rest/v1/Entities/{entityName}")
    
    @Common.LogFunction
    def DeleteEntities(self, entityNames:list[str]) -> dict[str, Any]:
        """_summary_

        Args:
            entityNames (list): List of entity names to delete

        Returns:
            dictionary: deletion information.
        """
        return self.CallAPI(RequestOperation.Delete, "rest/v1/Entities?Entities=" + ",".join(entityNames))


#############################################################################
## Events
#############################################################################
    def CallExternalEventNotification(self, event) :
        raise NotImplementedError("CallExternalEventNotification not implemented yet...")    
    # GET     CallExternalEventNotification

    def CancelUnprocessedEventMessages(self, subscriberConfigurationName) :
        raise NotImplementedError("CancelUnprocessedEventMessages not implemented yet...")    
    # POST    CancelUnprocessedEventMessages(subscriberConfigurationName)
    
    def TriggerInternalEvent(self, eventScenarioNames, record_codes, entityName) :
        raise NotImplementedError("TriggerInternalEvent not implemented yet...")        
    #POST    TriggerInternalEvent(eventScenarioNames[], record_c
    # odes[], entityName)


#############################################################################
## FileAttachment
#############################################################################
    def GetFileAttachment(self, entityName, recordCode, categoryName) :
        pass

    def PutFileAttachment(self, entityName, recordCode, categoryName) :
        pass

#############################################################################
## Forms
#############################################################################
    def GetForms(self, entityName = None) :
        pass
    
    def GetForm(self, formUid) :
        pass

#############################################################################
## Governance
#############################################################################

#############################################################################
# LogEvents
#############################################################################
    @Common.LogFunction
    def GetLogEvents(self, pageNumber = 1, pageSize = 50) :
        """Get log events in reverse chronological order with optional pagination arguments.

        Args:
            pageNumber (int, optional): Page number (starting at 1). Defaults to 1.
            pageSize (int, optional): Page size to return. Defaults to 50.

        Returns:
            dictionary: List of log events.
        """
        return self.CallAPI(RequestOperation.Get, f"rest/v1/LogEvents?PageNumber={pageNumber}&PageSize={pageSize}")

#############################################################################
# # Matching
#############################################################################
    @Common.LogFunction
    def GetMatchingStrategies(self) :
        """_summary_

        Returns:
            dictionary: List of matching strategies.
        """
        return self.CallAPI(RequestOperation.Get, "rest/v1/Matching")

    def GetMatches(self, strategyName, record_codes) :
        pass

    def Lookup(self) :
        pass

    @Common.LogFunction
    def ProcessMatchingActions(self, strategyName:str , processAction : ProcessActions) -> dict[str, Any]:
        actions = { "actions" : [] }
        match processAction :
            case ProcessActions.MatchingAndSurvivorship : actions = { "actions" : [ "IncludeSurvivorship" ] }
            case ProcessActions.SurvivorshipOnly : actions = { "actions" : [ "SurvivorshipOnly" ] }
            case ProcessActions.ClearPriorResults : actions = { "actions" : [ "ClearPriorResults", "ClearMatchingResults" ] }
            case ProcessActions.ClearAllPriorResults : actions = { "actions" : [ "ClearAllPriorResults", "ClearMatchingResults" ] }
        return self.CallAPI(RequestOperation.Post, f"rest/v1/Matching/{strategyName}/processActions", json = actions)
    
    @Common.LogFunction
    def RestartMatchingSequence(self, strategyName, value) :
        return self.CallAPI(RequestOperation.Post, f"rest/v1/Matching/{strategyName}/restartSequence?Value={value}")
        
    def Survivorship(self) :
        pass
        
    def Housekeeping(self) :
        pass
        
    def Match(self, strategyName, record_codes) :
        pass
        
    def UpdateMatchingStrategy(self, strategyName, matchingStatus : MatchingStatus) :
        status = { "continuousMatchingSetting" : matchingStatus.value }
        return self.CallAPI(RequestOperation.Patch, f"rest/v1/Matching/{strategyName}", json = status)
    
    @Common.LogFunction        
    def UnmatchRecords(self, strategyName, record_codes) :
        return self.CallAPI(RequestOperation.Patch, f"rest/v1/Matching/{strategyName}/unmatchRecords", json = { "record_codes" : record_codes })

#############################################################################
## Monitor
#############################################################################
    def GetMonitorActivities(self, getOptions : GetOptions = None) :
        if (getOptions is None) : 
            getOptions = GetOptions()
            getOptions.OrderBy = "[StartedTime] desc"
        return self.CallAPI(RequestOperation.Get, f"rest/v1/Monitor/activities?{getOptions.QueryString()}")
    
    def GetMonitorActivity(self, activityCode) :
        raise NotImplementedError("GetMonitorActivity not implemented yet...")        
    # GET     GetMonitorActivity(activityCode)
    
    def GetMonitorActivityDetail(self, activityCode, getOptions) :
        raise NotImplementedError("GetMonitorActivityDetail not implemented yet...")            
    # GET     GetMonitorActivityDetail(activityCode, getOptions)

#############################################################################
## Notifications
#############################################################################
    def SendNotification(self, description, notificationType, userNames, notificationTiming) :
        raise NotImplementedError("SendNotification not implemented yet...")       
    # POST    SendNotification(description, notificationType, userNames[], notificationTiming)

#############################################################################
## PortalConfiguration
#############################################################################
    def UpdatePortalIcon(self, icon) :
        pass
    
#############################################################################
## PresentationView
#############################################################################
    def GetDefaultPresentationView(self, entityName) :
        pass

    def GetPresentationView(self, entityUid, presentationViewUid) :
        pass

#############################################################################
## Records (Change Member to record for consistency)
#############################################################################    
    @Common.LogFunction
    # GET     GetMemberCloneAttributes(entityName, recordCode)
    def GetMemberCloneAttributes(self, entityName, recordCode) :
        pass

    @Common.LogFunction
    def GetRecord(self, entityName, recordCode) :
        """Calls GetRecords to get specific record from instance.

        Args:
            entityName (string): Entity name to get record from.
            recordCode (string_type_): Record code to get.

        Returns:
            dictionary: record
        """
        data = self.GetRecords(entityName, GetOptions(f"[Code] eq '{recordCode}'"))
        return data[0] if len(data) > 0 else None
    
    @Common.LogFunction
    def GetRecords(self, entityName, getOptions : GetOptions = None) :
        if (getOptions is None): getOptions = GetOptions()
        
        response = self.CallAPI(RequestOperation.Get, f"rest/v1/Records/{entityName}?{getOptions.QueryString()}")                
        return self.LastResponse.json() if getOptions.CountsOnly else response
    
    @Common.LogFunction
    def CreateRecord(self, entityName, record) :
        """_summary_

        Args:
            entityName (string): Entity name to create record in
            record (dictionary): Record to create

        Returns:
            dictionary: Creation information
        """
        return self.CallAPI(RequestOperation.Post, f"rest/v1/Records/{entityName}", record)
    
    @Common.LogFunction
    def MergeRecord(self, entityName, record) :
        return self.MergeRecords(entityName, [record])
    
    @Common.LogFunction
    def MergeRecords(self, entityName, records) :
        """Merge records into entity

        Args:
            entityName (string): Entity name
            records (list): List of records to merge into entity

        Returns:
            dictionary: Merge records information
        """
        return self.CallAPI(RequestOperation.Patch, f"rest/v1/Records/{entityName}", json=records)

    @Common.LogFunction
    def DeleteRecord(self, entityName: str, recordCode: str) :
        """Delete specified record from entity

        Args:
            entityName (string): Entity name
            recordCode (string): Record code to remove from entity

        Returns:
            dictionary: Delete records information
        """
        return self.DeleteRecords(entityName, [recordCode])
    
    @Common.LogFunction
    def DeleteRecords(self, entity_name: str, record_codes: list) :
        """Delete specified records

        Args:
            entityName (string): Entity name
            record_codes (list): List of record codes to remove from entity

        Returns:
            dictionary: Delete records information
        """
        # ToDo : If > x RecordCodes sent in batch the operation since we are sending the record codes via the url and it is limited to about 2000 characters
        return self.CallAPI(RequestOperation.Patch, f"rest/v1/Records/{entity_name}?Record_codes=" + ",".join(record_codes))
    
    @Common.LogFunction
    def DeleteAllMembers(self, entity_name:str) -> dict[str, Any]:
        """Deletes all members of a specific entity.

        Args:
            entity_name (str): The name of the entity to delete members from.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Delete, f"rest/v1/Records/bulk/{entity_name}")

#############################################################################
## Themes
#############################################################################
    def GetThemes(self) -> dict[str, Any]:
        """Retrieves all themes.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Get, "rest/v1/Themes")

    def GetTheme(self, theme_name:str) -> dict[str, Any]:
        """Retrieves a specific theme.

        Args:
            theme_name (str): The name of the theme to retrieve.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Get, f"rest/v1/Themes/{theme_name}")

    def UpdateTheme(self, theme_name:str, theme_object:dict[str, Any]) -> dict[str, Any]:
        """Updates a specific theme.

        Args:
            theme_name (str): The name of the theme to update.
            theme_object (dict[str, Any]): The updated theme object.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Put, f"rest/v1/Themes/{theme_name}", json=theme_object)

#############################################################################
## Transactions
#############################################################################
    def GetTransactions(self, entity_name:str, record_code:str, get_options:GetOptions) -> dict[str, Any]:
        """Retrieves transactions for a specific record.

        Args:
            entity_name (str): The name of the entity.
            record_code (str): The code of the record.
            get_options (GetOptions): Options for the GET request.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Get, f"rest/v1/Transactions/{entity_name}?recordCode={record_code}&{get_options.QueryString()}")

    def ReverseTransaction(self, entity_name:str, transaction_id:int, record_code:str) -> dict[str, Any]:
        """Reverses a specific transaction.

        Args:
            entity_name (str): The name of the entity.
            transaction_id (int): The ID of the transaction to reverse.
            record_code (str): The code of the record associated with the transaction.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        return self.CallAPI(RequestOperation.Put, f"rest/v1/Transactions/{entity_name}/{transaction_id}/reverse", json = { "recordCode": record_code })

#############################################################################
# Workflows
#############################################################################
    def DeleteWorkflowInstances(self, workflow_name:str, instance_status:WorkflowInstanceStatus) -> dict[str, Any]:
        """Deletes specified instances of a workflow.

        Args:
            workflow_name (str): The name of the workflow.
            instance_status (WorkflowInstanceStatus): The status of the instances to delete.

        Returns:
            dict[str, Any]: The response from the API call.
        """
        instance_status_query_part = f"&InstanceStatus={instance_status.value}" if instance_status != WorkflowInstanceStatus.All else ""
        return self.CallAPI(RequestOperation.Delete, f"rest/v1/Workflows?WorkflowName={workflow_name}{instance_status_query_part}")
