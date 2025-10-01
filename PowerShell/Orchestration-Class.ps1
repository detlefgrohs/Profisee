

enum DebugLogLevel {
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
}


class Orchestration {
    [ProfiseeRestful] $API;
    [string] $OrchestrationEntityName;
    [string] $OrchestrationStepEntityName;
    [string] $OrchestrationLogEntityName;

    [DebugLogLevel] $MinLogLevel = [DebugLogLevel]::Info;
    [int] $ActivityPollingInterval = 15;

    [switch] $bootstrap = $false;

    [bool] $what_if;

    [System.Array] $Results = @();


    Orchestration($API, $OrchestrationEntityName) {
        $this.API = $API;
        $this.OrchestrationEntityName = $OrchestrationEntityName;
        $this.OrchestrationStepEntityName = $OrchestrationEntityName + "Step";
        $this.OrchestrationLogEntityName = $OrchestrationEntityName + "Log";
        $this.what_if = $false;

        $this.GetOrchestrationSettings();
    }

    [void] GetOrchestrationSettings() {
        $settings_record = $this.API.GetRecord($this.OrchestrationEntityName, "z_Settings");
        $settings = $settings_record.Parameters | ConvertFrom-Json;

        if ($settings -ne $null) {
            $this.MinLogLevel = [DebugLogLevel]$settings.MinLogLevel;
            $this.ActivityPollingInterval = $settings.ActivityPollingInterval;
        } else {
            Write-Host "Failed to retrieve orchestration settings from '$($this.OrchestrationEntityName)'. Exiting."
            exit(1)
        }
    }

    [object] GetOrchestrationSteps($orchestration_code) {
        $options = [GetOptions]::new();
        $options.Filter = "[$($this.OrchestrationEntityName)] eq '$($orchestration_code)'"
        $options.OrderBy = "[StepNumber]"

        return $this.API.GetRecords($this.OrchestrationStepEntityName, $options);
    }

    [System.Array] GetOrchestration($orchestration_code) {
        $orchestration = $this.API.GetRecord($this.OrchestrationEntityName, $orchestration_code);
        return $orchestration, ($orchestration.Parameters | ConvertFrom-Json);
    }

    [object] Orchestrate($orchestration_code) {
        $this.LogToProfisee($orchestration_code, $null, "DEBUG", "Orchestrate($($orchestration_code))")
        $orchestration, $orchestration_parameters = $this.GetOrchestration($orchestration_code);
        if ($orchestration -eq $null) {
            return @{
                "Error" = $true;
                "Message" = "Orchestration '$($orchestration_code)' not found.";
            }
        }

        $threaded = $orchestration_parameters.Mode -eq "Concurrent";
        $abort_on_error = $orchestration_parameters.ErrorHandling -eq "Abort";

        $this.LogToProfisee($orchestration.Code, $null, "INFO", "Starting orchestration '$($orchestration_code)' in mode '$($orchestration_parameters.Mode)' with error handling '$($orchestration_parameters.ErrorHandling)'...");

        $threads = @();
        $this.Results = @();

        $this.GetOrchestrationSteps($orchestration.Code) | ForEach-Object {
            $orchestration_step = $_
            
            $this.LogToProfisee($orchestration_code, $null, "DEBUG", "OrchestrationStep($($orchestration_step))")

            $strategy_name = $orchestration_step.Name
            $orchestration_step_code = $orchestration_step.Code
            $process_type = $orchestration_step.ProcessType
            $parameters = $orchestration_step.Parameters | ConvertFrom-Json

            if ($parameters -eq $null) {
                $parameters = @{}
            }

            if ($parameters.Enabled -eq $null -or $parameters.Enabled -eq $true) {
                if ($threaded) {

                } else {

                }
                # ToDo: Implement threading
                $result = $this.Run($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters);
                
                if ($abort_on_error -and $result.Error -eq $true) {
                    $this.LogToProfisee($orchestration.Code, $orchestration_step_code, "ERROR", "Aborting orchestration '$($Name)' due to error in step '$($orchestration_step_code)' '$($strategy_name)'.");
                    break;
                    # return @{
                    #     "Error" = $true;
                    #     "Message" = "Orchestration '$($Name)' aborted due to error in step '$($orchestration_step_code)' '$($strategy_name)'.";
                    # }
                }

            } else {
                $this.LogToProfisee($orchestration.Code, $orchestration_step_code, "INFO", "Skipping disabled step '$($orchestration_step_code)' '$($strategy_name)'...");
            }

        }

        if ($threaded) {
            # Wait for all threads to complete
        }

        $overall_error = $false;
        foreach ($result in $this.Results) {
            if ($result.Error -eq $true) {
                $overall_error = $true;
                break;
            }
        }

        if ($overall_error) {
            $this.LogToProfisee($orchestration.Code, $null, "ERROR", "Orchestration '$($orchestration_code)' completed with errors.");
        } else {
            $this.LogToProfisee($orchestration.Code, $null, "INFO", "Orchestration '$($orchestration_code)' completed successfully.");
        }

        $return_value = @{
            "Orchestration" = $orchestration_code;
            "Error" = $overall_error;
            "Results" = $this.Results;
        }
        $this.LogToProfisee($orchestration_code, $null, "DEBUG", "Orchestrate() => $($return_value | ConvertTo-Json)")
        return $return_value;
    }

    [object] Run($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters) {
        $this.LogToProfisee($orchestration_code, $orchestration_step_code, "DEBUG", "Run()")

        $since_datetime = (Get-Date -AsUTC)
        $run_errored = $false;

        $start_process_result = $this.StartProcess($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters);
        $this.LogToProfisee($orchestration_code, $orchestration_step_code, "DEBUG", "start_process_result = '$($start_process_result | ConvertTo-Json)'")

        if ($null -eq $start_process_result -or $start_process_result.Error -eq $false) {
            $wait_for_completion_result = $this.WaitForCompletion($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters, $since_datetime);
            Write-Host ($wait_for_completion_result | ConvertTo-Json)

            $run_errored = $wait_for_completion_result.Error;
        } else {
            $run_errored = $true
        }

        $result = @{
            "Orchestration" = $orchestration_code;
            "OrchestrationStep" = $orchestration_step_code;
            "StrategyName" = $strategy_name;
            "ProcessType" = $process_type;
            "Parameters" = $parameters;
            "Error" = $run_errored;
            "Message" = "Running orchestration step '$($orchestration_step_code)' '$($strategy_name)' with process type '$($process_type)'.";
        }
        $this.Results += $result;
        return $result
    }

    [object] StartProcess($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters) {

        if ($process_type.ToLower() -eq "connect") {
            return $this.StartProcessConnect($orchestration_code, $orchestration_step_code, $strategy_name, $parameters);
        } elseif ($process_type.ToLower() -eq "matching") {
            return $this.StartProcessMatching($orchestration_code, $orchestration_step_code, $strategy_name, $parameters);
        } else {
            return @{
                "Error" = $true;
                "Message" = "Unknown process type '$($process_type)' for step '$($orchestration_step_code)' '$($strategy_name)'.";
            }
        }
    }

    [object] StartProcessConnect($orchestration_code, $orchestration_step_code, $strategy_name, $parameters) {
        if ($this.what_if) {
            $this.LogToProfisee($orchestration_code, $orchestration_step_code, "INFO", "(WhatIf) Starting Connect process '$($strategy_name)' with parameters: $(ConvertTo-Json -InputObject $parameters)");
            return @{
                "Error" = $false;
                "Response" = $null            
            }
        }

        $response = $this.API.RunConnectBatch($strategy_name, "", @());  # ToDo: Add Filters
        # Check for error...
        return @{
            "Error" = $false;
            "Response" = $response
        }
    }

    [object] StartProcessMatching($orchestration_code, $orchestration_step_code, $strategy_name, $parameters) {
        if ($this.what_if) {
            $this.LogToProfisee($orchestration_code, $orchestration_step_code, "INFO", "(WhatIf) Starting Matching process '$($strategy_name)' with parameters: $(ConvertTo-Json -InputObject $parameters)");
            return @{
                "Error" = $false;
                "Response" = $null
            }
        }

        # ToDo: Implement ProcessActions
        $process_action = [ProcessActions]::MatchingOnly
        $response = $this.API.ProcessMatchingActions($strategy_name, $process_action);  # ToDo: Add Filters
        # Check for error...
        return @{
            "Error" = $false;
            "Response" = $response
        }
    }

    [string] GetActivityTypeForProcessType($process_type, $parameters) {
        $activity_type = $parameters.ActivityType
        if ($process_type.ToLower() -eq "connect") {
            if ([System.String]::IsNullOrEmpty($activity_type)) { return "Connect Strategy Execution" }
        } elseif ($process_type.ToLower() -eq "matching") {
            if ([System.String]::IsNullOrEmpty($activity_type)) { return "Clustering & Survivorship" }
        }
        return $activity_type
    }

    [object] WaitForCompletion($orchestration_code, $orchestration_step_code, $strategy_name, $process_type, $parameters, $since_datetime) {
        $this.LogToProfisee($orchestration_code, $orchestration_step_code, "DEBUG", "WaitForCompletion()")
        
        if ($this.what_if) {
            $this.LogToProfisee($orchestration_code, $orchestration_step_code, "INFO", "(WhatIf) Waiting for completion of process type '$($process_type)' for step '$($orchestration_step_code)' '$($strategy_name)'...");
            return @{
                "FirstActivityDateTime" = (Get-Date);
                "ElapsedTime" = (Get-Date) - (Get-Date)
                "Error" = $false;
                "Activities" = @();
            }
        }

        $first_activity_datetime = $null;
        $was_successful = $false;

        $activity_type = $this.GetActivityTypeForProcessType($process_type, $parameters);
        $since_datetime_as_string = $since_datetime.ToString("yyyy-MM-ddTHH:mm:ssZ");

        $get_options = [GetOptions]::new();
        #$get_options.Filter = "contains([Name], '$($strategy_name)') and [ActivityType] eq '$($activity_type)' and [Service] eq '$($process_type)' and [StartedTime] gt $($since_datetime_as_string)"
        $get_options.Filter = "[ActivityType] eq '$($activity_type)' and [Service] eq '$($process_type)' and [StartedTime] gt $($since_datetime_as_string)"
        
        Write-Host $get_options.Filter
        $this.LogToProfisee($orchestration_code, $orchestration_step_code, "DEBUG", "get_options = $($get_options.GetQueryStrings())")

        $monitor_activities = @()
        while ($true) {
            $monitor_activities = $this.API.GetMonitorActivities($get_options);

            if ($monitor_activities.Count -gt 0) {
                if ($null -eq $first_activity_datetime) { $first_activity_datetime = (Get-Date)}

                $number_of_not_running = 0
                $number_of_succeeded = 0

                $monitor_activities | ForEach-Object {
                    $monitor_activity = $_

                    $status = $monitor_activity.Status

                    if ($status -ne "Running") { 
                        $number_of_not_running += 1
                    }

                    if ($status -eq "Succeeded") {
                        $number_of_succeeded += 1
                    }
                }

                if ($monitor_activities.Count -eq $number_of_not_running) {
                    if ($number_of_succeeded -eq $monitor_activities.Count) {
                        $was_successful = $true
                    }
                    break;
                }
            }

            Start-Sleep -Seconds $this.ActivityPollingInterval
        }
        
        return @{
            "FirstActivityDateTime" = $first_activity_datetime;
            "ElapsedTime" = (Get-Date) - $first_activity_datetime;
            "Error" = -not $was_successful;
            "Activities" = $monitor_activities;
        }
    }

    [bool] ShouldLog($log_level) {
        return $log_level -ge $this.MinLogLevel;
    }

    [void] LogToProfisee($orchestration_code, $orchestration_step_code, $log_level, $message) {
        if ($this.ShouldLog([DebugLogLevel]$log_level)) {
            Write-Host "$() [$($log_level)] : $($orchestration_code) $($orchestration_step_code) $($message)"

            $log_record = @{
                $this.OrchestrationEntityName = $orchestration_code;
                $this.OrchestrationStepEntityName = $orchestration_step_code;
                "LogLevel" = $log_level;
                "Message" = $message;
            }
            $this.API.MergeRecord($this.OrchestrationLogEntityName, $log_record);
        }
    }

    [object] WrapWithTryCatch([ScriptBlock] $ScriptBlock) {
        try {

            $return_value = & $ScriptBlock;

            return $return_value;
        } catch {
            # $exceptionMessage = ($this.HandleRestException($_))
            # $this.LogMessage("Exception: $($exceptionMessage)", [LogType]::Error);
            # $this.LastResponse = $exceptionMessage;
            # # DG ToDo: if $exceptionMessage is null create another response...
            return $null
        }
        return $null;
    }

}