enum DbaFormatType { Default = 0; CodeOnly = 1; CodeAndName = 2 }
enum ProcessActions {
    MatchingOnly = 0
    MatchingAndSurvivorship = 1
    SurvivorshipOnly = 2
    ClearPriorResults = 3
    ClearAllPriorResults = 4
}

class GetOptions {
    [string]$Filter = "";
    [string]$OrderBy = "";
    [string[]]$Attributes = @();
    [DbaFormatType]$DbaFormat = [DbaFormatType]::Default;
    [bool]$CountsOnly = $false;
    [int]$PageNumber = 1;
    [int]$PageSize = 50;

    GetOptions() {}
    GetOptions($filter) { $this.Filter = $filter; }

    [string] GetQueryStrings() {
        $queryStrings = New-Object System.Collections.Generic.List[string];
        if ($this.Filter -ne "") { $queryStrings += "Filter=$([System.Net.WebUtility]::UrlEncode($this.Filter))" }
        if ($this.PageNumber -ne 1) { $queryStrings += "PageNumber=$($this.PageNumber)" }
        if ($this.PageSize -ne 50) { $queryStrings += "PageSize=$($this.PageSize)" }
        if ($this.OrderBy -ne "") { $queryStrings += "OrderBy=$($this.OrderBy)" }
        if ($this.Attributes.Count -gt 0) { $queryStrings += "Attributes=$([String]::Join(',', $this.Attributes))" }
        if ($this.DbaFormat -ne [DbaFormatType]::Default) { $queryStrings += "DbaFormat=$([int]$this.DbaFormat)" }
        if ($this.CountsOnly) { $queryStrings += "CountsOnly=true" }
        return [string]::Join("&", $queryStrings);
    }
}

enum LogType { Debug; Info; Error }

class ProfiseeRestful {
    [string]$ProfiseeUri;
    [string]$ClientId;
    $Logger;
    $LastResponse;
    [bool]$LogData = $false;
    [LogType]$LogLevel = [LogType]::Info;

    ProfiseeRestful($Environment) {
        $Settings = ((Get-Content "$Global:ExecutionDirectory\settings.json") | ConvertFrom-Json)
        $this.Setup($($Settings.Environments.$Environment.ProfiseeURI), $($Settings.Environments.$Environment.ClientID));
    }
    ProfiseeRestful($profiseeUri, $clientId) {
        $this.Setup($profiseeUri, $clientId);
    }

    [void] Setup($profiseeUri, $clientId) {
        $this.LogMessage("ProfiseeRestful($($profiseeUri), $($clientId))", [LogType]::Info);
        $this.ProfiseeUri = $profiseeUri;
        $this.ClientId = $clientId;
    }

    [bool] Errored() {
        if ($this.LastResponse.errors -ne $null) { return $true; }
        return $false;
    }


    [object] GetConnectServiceProviders() {
        $this.LogMessage("GetConnectServiceProviders()", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/ServiceProviders") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                #if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    [object] GetConnectServiceProviderSpecification($serviceProviderName) {
        $this.LogMessage("GetConnectServiceProviderSpecification($($serviceProviderName))", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/ServiceProviders/$($serviceProviderName)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                #$this.DumpProfiseeData();
    
                return $this.LastResponse;
            });
    }

    [object] GetConnectConfigurations() {
        $this.LogMessage("GetConnectConfigurations()", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/Configurations") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                #if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    [object] GetConnectConfiguration($configurationName) {
        $this.LogMessage("GetConnectConfiguration($($configurationName))", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/Configurations/$($configurationName)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                #$this.DumpProfiseeData();
    
                return $this.LastResponse;
            });
    }

    [object] GetConnectStrategies() {
        $this.LogMessage("GetConnectStrategies()", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/Strategies") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                #if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    [object] GetConnectStrategy($strategyName) {
        $this.LogMessage("GetConnectStrategy($($strategyName))", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/Strategies/$($strategyName)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                #$this.DumpProfiseeData();
    
                return $this.LastResponse;
            });
    }

    [object] RunConnectBatch($strategyName, $filter = "", $recordCodes = @()) {
        $this.LogMessage("GetConnectStrategy($($strategyName))", [LogType]::Info);

        $body = @{
            FilterExpression = $filter
            Codes = $recordCodes
        }
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Connect/Strategies/$($strategyName)/Batch") `
                    -Method POST `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json $body)
                $this.LogMessage("   Method = POST", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                #$this.DumpProfiseeData();
    
                return $this.LastResponse;
            });
    }
    
    #########################################################################
    # AddressVerificationStrategies
    #########################################################################
    # GetAddressVerificationStrategies

    [object] GetAddressVerificationStrategies() {
        $this.LogMessage("GetAddressVerificationStrategies()", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("AddressVerificationStrategies") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                return (, $this.LastResponse.data);
            });
    }
        
    # GetAddressVerificationStrategy
    [object] GetAddressVerificationStrategy($StrategyName) {
        $this.LogMessage("GetAddressVerificationStrategy($($StrategyName))", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("AddressVerificationStrategies/$($StrategyName)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                return $this.LastResponse;
            });
    }
    # GetAddressVerificationStrategy
    [object] GetAddressVerificationStrategyResults($StrategyName, $Code) {
        $this.LogMessage("GetAddressVerificationStrategyResults($($StrategyName), $($Code))", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("AddressVerificationStrategies/$($StrategyName)/address?recordCode=$($Code)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    # StartAddressVerificationStrategy
    # CancelAddressVerificationStrategy

    #########################################################################
    # Auth
    #########################################################################
    # GetAuthenticationUrl
    #   \Auth
    #   No Header needed...

    #########################################################################
    # DataQualityRules
    #########################################################################
    # GetDataQualityRules
    # GetOperatorTypes

    #########################################################################
    # Events
    #########################################################################
    # ???

    #########################################################################
    # Forms
    #########################################################################
    # GetForms
    # GetForm

    #########################################################################
    # Governance
    #########################################################################
    # ???
    #

    [object] GetMonitorActivities([GetOptions]$GetOptions) {
        $this.LogMessage("GetMonitorActivities(GetOptions = '$($GetOptions.GetQueryStrings())')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Monitor/activities?$($GetOptions.GetQueryStrings())") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    #########################################################################
    # Matching
    #########################################################################    
    # GetMatchingStrategies
    # MatchMember
    # LookupMember
    # ProcessMatchingStrategy
    # SurviveMatchingStrategy
    # ProcessMatchingStrategyForMember
    # UnmatchRecord
    [object] UnmatchRecords($StrategyName, $Codes) {
        $this.LogMessage("UnmatchRecords(StrategyName = '$($StrategyName)', Codes = '$($Codes)')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod `
                    -Uri $this.GetProfiseeRESTfulUri("Matching/$($StrategyName)/unmatchRecords") `
                    -Method Patch `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json @{ recordCodes = @( $Codes ) })
                $this.LogMessage("   Method = PATCH", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                return (, $this.LastResponse.data);
            });
    }


    [object] ProcessMatchingActions($StrategyName, [ProcessActions] $processAction) {
        $this.LogMessage("ProcessMatchingActions(StrategyName = '$($StrategyName)', ProcessAction = '$($processAction)')", [LogType]::Info);
    
        $actions = @{ "actions" = @() }
        switch ($processAction) {
            "MatchingAndSurvivorship" { $actions = @{ "actions" = @( "IncludeSurvivorship" ) } }
            "SurvivorshipOnly" { $actions = @{ "actions" = @( "SurvivorshipOnly" ) } }
            "ClearPriorResults" { $actions = @{ "actions" = @( "ClearPriorResults", "ClearMatchingResults" ) } }
            "ClearAllPriorResults" { $actions = @{ "actions" = @( "ClearAllPriorResults", "ClearMatchingResults" ) } }
        }

        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod `
                    -Uri $this.GetProfiseeRESTfulUri("Matching/$($StrategyName)/processActions") `
                    -Method Post `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json $actions)
                $this.LogMessage("   Method = POST", [LogType]::Debug);
                $this.LogMessage("   Body - $((ConvertTo-Json $actions))", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                return (, $this.LastResponse.data);
            });
    }

    #########################################################################
    # Notifications
    #########################################################################
    # SendNotification
    #   Description
    #   NotificationType
    #   Users
    #   NotificationTiming
    # Many more

    #########################################################################
    # PortalConfiguration
    #########################################################################
    # UpdatePortalIcon

    #########################################################################
    # PresentationView
    #########################################################################
    # Get

    #########################################################################
    # Themes
    #########################################################################
    # Get
    # UpdateTheme


    #########################################################################
    # Transactions
    #########################################################################
    # Get
    [object] GetTransactions($Entity, $Code, $PageSize = 50) {
        $this.LogMessage("GetTransactions(Entity = '$($Entity)', Code = '$($Code)')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Transactions/$($Entity)?recordCode=$($Code)&pageSize=$($pageSize)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();

                return (, $this.LastResponse.data);
            });
    }
    # PUT Reverse


    #########################################################################
    # Workflows
    #########################################################################
    # DeleteWorkflows
    # \Workflows?WorkflowName={name}
    # \Workflows?WorkflowName={name}&InstanceStatus=x

    #########################################################################
    # Records
    #########################################################################
    [object] GetRecord($Entity, $Code) {
        $this.LogMessage("GetRecord(Entity = '$($Entity)', Code = '$($Code)')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Records/$($Entity)/$($Code)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
                return $this.LastResponse.data[0]                                         
            });
    }

    [object] GetRecords($Entity, [GetOptions]$GetOptions) {
        $this.LogMessage("GetRecords(Entity = '$($Entity)', GetOptions = '$($GetOptions.GetQueryStrings())')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $this.LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Records/$($Entity)?$($GetOptions.GetQueryStrings())") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader()
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
    
                if ($GetOptions.CountsOnly -eq $true) { return $this.LastResponse; }
                return (, $this.LastResponse.data);
            });
    }

    [object] MergeRecord($Entity, $Body) {
        return $this.MergeRecords($Entity, @($Body));
    }

    [object] MergeRecords($Entity, $Body) {
        $this.LogMessage("MergeRecords(Entity = '$($Entity)')", [LogType]::Info);
        $index = 0;
        $logType = [LogType]::Debug;
        if ($this.LogData) { $logType = [LogType]::Info; }
        $Body | ForEach-Object {
            $this.LogMessage("   Member[$($index)]", $logType);
            $this.DumpBody($_);
            $index += 1;
        }

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Records/$($Entity)") `
                    -Method PATCH `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json $Body);
                $this.LogMessage("   Method = PATCH", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                $this.DumpProfiseeData();
                return $Global:LastResponse;
            });
    }
    
    [object] DeleteRecord($Entity, $Code) {
        $this.LogMessage("DeleteRecord(Entity = '$($Entity)', Code = '$($Code)')", [LogType]::Info);
    
        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Records/$($Entity)?RecordCodes=$($Code)") `
                    -Method DELETE `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = DELETE", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();
                return $Global:LastResponse;                        
            });
    }
    
    [object] DeleteRecords($Entity, $Codes) {
        $this.LogMessage("DeleteRecords(Entity = '$($Entity)', Codes = '$([String]::Join(',', $Codes))')", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Records/$($Entity)?RecordCodes=$($Codes -join ',')") `
                    -Method DELETE `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = DELETE", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return $Global:LastResponse;    
            });
    }
    #########################################################################
    # MetaModel
    #   Entities
    #   Attributes
    #########################################################################
    [object] GetEntities() {
        $this.LogMessage("GetEntities()", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Entities") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);
            });
    }
    [object] GetAttributes($Entity) {
        $this.LogMessage("GetAttributes(Entity = '$($Entity)')", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Entities/$($Entity)/attributes") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);  
            });
    }

    [object] UpdateAttributes($Body) {
        $this.LogMessage("UpdateAttributes()", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Attributes") `
                    -Method PUT `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json $Body -Depth 100);
                $this.LogMessage("   Method = PUT", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);  
            });
    }

    [object] GetDataQualityRules() {
        $this.LogMessage("GetDataQualityRules()", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Rules") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);
            });
    }

    [object] GetDataQualityRule($Uid) {
        $this.LogMessage("GetDataQualityRule($($Uid))", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Rules/$($Uid)") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return $Global:LastResponse;
            });
    }

    [object] MergeDataQualityRules($Body) {
        $this.LogMessage("MergeDataQualityRules()", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("Rules") `
                    -Method PUT `
                    -Headers $this.GetProfiseeRESTfulHeader() `
                    -Body (ConvertTo-Json $Body -Depth 100);
                $this.LogMessage("   Method = PUT", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);
            });
    }

    #########################################################################
    # LogEvents
    #########################################################################
    [object] GetLogEvents() {
        $this.LogMessage("GetLogEvents()", [LogType]::Info);

        return $this.WrapWithTryCatch({
                $Global:LastResponse = Invoke-RestMethod -Uri $this.GetProfiseeRESTfulUri("LogEvents?PageNumber=1&PageSize=50") `
                    -Method GET `
                    -Headers $this.GetProfiseeRESTfulHeader() 
                $this.LogMessage("   Method = GET", [LogType]::Debug);
                $this.LogMessage("   Response = '$($this.LastResponse)'", [LogType]::Debug);
                $this.DumpProfiseeErrors();    
                return (, $Global:LastResponse.data);  
            });
    }

    #########################################################################
    # Logging
    #########################################################################
    [void] LogMessage($Message, [LogType]$LogType) {
        $logMessage = $false;
        if ($this.LogLevel -eq [LogType]::Debug) { $logMessage = $true; }
        if ($this.LogLevel -eq [LogType]::Info) { if ($LogType -eq [LogType]::Info -or $LogType -eq [LogType]::Error) { $logMessage = $true; } }
        if ($this.LogLevel -eq [LogType]::Error) { if ($LogType -eq [LogType]::Error) { $logMessage = $true; } }       


        if ($logMessage) {
            (Get-Date).ToString("yyyyMMdd-hhmmss") + "|$($LogType)|$($Message)" | Add-Content "ProfiseeRESTful.log"
        }
    }

    #########################################################################
    # Utility
    #########################################################################
    [object] HandleRestException($Exception) {
        #return $this.WrapWithTryCatch({
        try {
            $result = $Exception.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($result)
            $reader.BaseStream.Position = 0
            $reader.DiscardBufferedData()
            return ($reader.ReadToEnd() | ConvertFrom-Json);
        }
        catch {
            Write-Host "   Exception in HandleRestException. $($_)"
            Write-Host "   Original Exception: $($Exception)"
        }
        #});
        return $null;
    }

    [object] WrapWithTryCatch([ScriptBlock] $ScriptBlock) {
        try {
            return & @ScriptBlock
        }
        catch {
            $exceptionMessage = ($this.HandleRestException($_))
            $this.LogMessage("Exception: $($exceptionMessage)", [LogType]::Error);
            $this.LastResponse = $exceptionMessage;
            # DG ToDo: if $exceptionMessage is null create another response...
            return $exceptionMessage
        }
        return $null;
    }

    [object] GetProfiseeRESTfulUri($Path) {
        $url = "$($this.ProfiseeUri)/rest/v1/$($Path)"
        $this.LogMessage("   ProfiseeUrl = '$($url)'", [LogType]::Debug);
        return $url;
    }

    [object] GetProfiseeRESTfulHeader() {
        $header = @{ 
            'x-api-key'    = $this.ClientId
            # 'Content-Type' = 'application/json-patch+json'
            'Content-Type' = 'application/json'
        };
        $header.Keys | ForEach-Object {
            $this.LogMessage("   Header: $($_) = '$($header[$_])'", [LogType]::Debug);
        }
        return $header;
    }

    [void] DumpProfiseeErrors() {
        if ($this.LastResponse.errors.Count -gt 0) {
            $index = 0;
            $this.LastResponse.errors | ForEach-Object {
                $this.LogMessage("   Error[$($index)] = '$($_)'", [LogType]::Error);
                $index += 1;
            }
        }
    }
    [void] DumpProfiseeData() {
        $index = 0;
        $this.LastResponse.data | ForEach-Object {
            $logType = [LogType]::Debug;
            if ($this.LogData) { $logType = [LogType]::Info; }
            $this.LogMessage("   Data[$($index)] = '$($_)'", $logType);
            $index += 1;
        }
    }

    [void] DumpCreatedRecordCodes() {
        $index = 0;
        $this.LastResponse.createdRecordCodes | ForEach-Object {
            $this.LogMessage("   Data[$($index)] = '$($_)'", [LogType]::Debug);
            $index += 1;
        }
    }
    [void] DumpBody($Body) {
        $index = 0;
        $Body.Keys | ForEach-Object {
            $logType = [LogType]::Debug;
            if ($this.LogData) { $logType = [LogType]::Info; }
            $this.LogMessage("      Body[$($index)]: $($_) = '$($Body[$_])'", $logType);
            $index += 1;
        }
    }
    [void] ForceDumpBody($Body) {
        $index = 0;
        $Body.Keys | ForEach-Object {
            $this.LogMessage("      Body[$($index)]: $($_) = '$($Body[$_])'", [LogType]::Info);
            $index += 1;
        }
    }
}