

class OrchestrationRunner {
    $API;

    OrchestrationRunner($API) {
        $this.API = $API;
    }

    [object] Orchestrate($Name) {
        $options = [GetOptions]::new();
        $options.Filter ="[Name] eq '$($Name)'"
        $options.OrderBy = "[Step]"

        $orchestrationSteps = $this.API.GetRecords("z_Orchestration", $options);
        if ($orchestrationSteps.Count -gt 0) {
            for ($index = 0; $index -lt $orchestrationSteps.Count; $index++) {
                $orchestrationStep = $orchestrationSteps[$index]
            #}
            #$orchestrationSteps | ForEach-Object {
                $name = $orchestrationStep.Name
                $code = $orchestrationStep.Code
                $step = $orchestrationStep.Step
                $process_type = $orchestrationStep.ProcessType
                $parameters = $orchestrationStep.Parameters

                $message = "Running step $($step) of orchestration '$($name)' of process_type '$($process_type)' with parameters '$($parameters)'..."
                $this.Log($code, "Info", $message);

                $parameters = ConvertFrom-Json -InputObject $parameters
                # Write-Host $parameters
                $response = $this.Run($process_type, $parameters);
                if ($response -ne $null -and $response.WasSuccessful -eq $false) {
                    $message = "Step $($step) of orchestration '$($name)' failed."
                    $this.Log($code, "Error", $message);
                    return @{
                        "Orchestration" = $orchestrationSteps;
                        "Response" = $response;
                    }
                }

                $message = "Step $($step) of orchestration '$($name)' completed successfully. $(ConvertTo-Json -InputObject $response)"
                $this.Log($code, "Info", $message);

                $message = "Completed step $($step) of orchestration '$($name)'."
                $this.Log($code, "Info", $message);
            }
        } else {
            # No steps found
        }


        return @{
            "Orchestration" = $orchestrationSteps;
            "Response" = $null;
        }
    }

    [object] Run($process_type, $parameters) {
        $filter = "";
        $activity_type = "";
        $service = "";
        $strategy_name = "";
        $monitor_activities = @()

        if ($process_type -eq "Connect") {
            $activity_type = "Default Activity"
            $service = "Connect"
            $strategy_name = $parameters.Name
            $filter = $parameters.Filter
        } elseif ($process_type -eq "Matching") {
            $activity_type = "Clustering %26 Survivorship"
            $service = "Matching"
            $strategy_name = $parameters.Name        
        } else {
            Write-Host "Unknown orchestration process_type '$($process_type)'"
            return $null;
        }

        if ($parameters.ActivityType -ne $null -and $parameters.ActivityType -ne "") { # Overwrite ActivityType if provided
            $activity_type = $parameters.ActivityType
        }   

        $since_datetime = (Get-Date -AsUTC)

        $options = [GetOptions]::new();
        $options.Filter = "[ActivityType] eq '$($activity_type)' and [Service] eq '$($service)' and [StartedTime] gt $($since_datetime.ToString("yyyy-MM-ddTHH:mm:ssZ"))"
        $was_successful = $false
        $first_activity_datetime = $null

        # Start Process
        if ($process_type -eq "Connect") {
            Write-Host "Running Connect batch for strategy '$($strategy_name)'..."
            $response = $this.API.RunConnectBatch($strategy_name, $filter, @())
        } elseif ($process_type -eq "Matching") {
                $response = $this.API.ProcessMatchingActions($strategy_name, [ProcessActions]::MatchingAndSurvivorship)
        } else {
            Write-Host "Unknown orchestration process_type '$($process_type)'"
            return $null;
        }

        while ($true) {
            $monitor_activities = $this.API.GetMonitorActivities($options)

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

    [void] Log($code, $type, $message) {
        Write-Host $message

        $log_entry = @{
            "z_Orchestration" = $code;
            "Type" = $type;
            "Message" = $message;
        }
        $response = $this.API.MergeRecord("z_OrchestrationLog", $log_entry);
    }
}