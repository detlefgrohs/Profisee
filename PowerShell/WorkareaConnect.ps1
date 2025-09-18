param($Environment = "Local")

$Global:ExecutionDirectory = Split-Path $MyInvocation.MyCommand.Path -Parent

. "$Global:ExecutionDirectory\ProfiseeRESTful.ps1"
. "$Global:ExecutionDirectory\Common-Functions.ps1"

$Global:Settings = ((Get-Content "$executionDirectory\settings.json") | ConvertFrom-Json)

$api = [ProfiseeRestful]::new($Environment);



function RunConnectBatch {
    param($activity_type, $service, $strategy_name)

    Write-Host "Running Connect batch for strategy '$($strategy_name)'..."

    $since_datetime = (Get-Date -AsUTC)

    $options = [GetOptions]::new();
    # $options.Filter = "[ActivityType] eq '{activity_type}' and [Service] eq '{service}' and [StartedTime] gt {since_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    $options.Filter = "[ActivityType] eq '$($activity_type)' and [Service] eq '$($service)' and [StartedTime] gt $($since_datetime.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
    $was_successful = $false
    $first_activity_datetime = $null

    $response = $api.RunConnectBatch($strategy_name, "", @())

    while ($true) {
        $monitor_activities = $api.GetMonitorActivities($options)

        # Now apply the name filter since we cannot do that in the API call
        $monitor_activities = $monitor_activities | Where-Object { 
            $_.Name -match [regex]::Escape($strategy_name)
        }

        if ($monitor_activities.Count -gt 0) {
        
            if ($first_activity_datetime -eq $null) {
                $first_activity_datetime = Get-Date
            }   

            $number_of_not_running = 0
            $number_of_succeeded = 0
            foreach ($activity in $monitor_activities) {
                $status = $activity.Status
                if ($status -eq "Cancelled" -or $status -eq "Failed" -or $status -eq "Succeeded") {
                    $number_of_not_running += 1
                }
                if ($status -eq "Succeeded") {
                    $number_of_succeeded += 1        
                }        
            }
            #Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') : Found $($monitor_activities.Count) activities, $number_of_not_running completed/failed/cancelled"        
            
            if ($monitor_activities.Count -gt 0 -and $monitor_activities.Count -eq $number_of_not_running) {
                if ($number_of_succeeded -eq $monitor_activities.Count) {           
                    $was_successful = $true
                } else {
                    $was_successful = $false
                }
                break
            }
        }
        Start-Sleep -Seconds 5    
    }

    return @{
        "FirstActivityDateTime" = $first_activity_datetime
        "ElapsedTime" = (Get-Date -AsUTC) - $since_datetime
        "NumberOfActivities" = $monitor_activities.Count
        "WasSuccessful" = $was_successful
        "Activities" = $monitor_activities
    }
}

$activity_type = "Database Export Activity"
$service = "Connect"
$strategy_name = "SQL Server [DQParent] Export [dbo].[tbl_DQParent]"

$response = RunConnectBatch $activity_type $service $strategy_name
$response

$strategy_name = "SQL Server [DQChild] Export [dbo].[tbl_DQChild]"

# $response = RunConnectBatch $activity_type $service $strategy_name
$response

/*

{ "Name" : "SQL Server [DQParent] Export [dbo].[tbl_DQParent]", "ActivityType" : "Database Export Activity" }

{ "Name" : "SQL Server [DQChild] Export [dbo].[tbl_DQChild]", "ActivityType" : "Database Export Activity" }

*/