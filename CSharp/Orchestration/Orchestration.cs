using Newtonsoft.Json;
using Profisee.MDM;
using System;

namespace Profisee.MDM {
    public class Orchestration {
        private RestfulAPI _api;
        private string OrchestrationEntityName = "Orchestration";
        private string OrchestrationStepEntityName = "OrchestrationStep";
        private string OrchestrationLogEntityName = "OrchestrationLog";
        public bool WhatIf { get; set; } = false;
        public LogLevel MinLogLevel = LogLevel.Information;
        private int ActivityPollingInterval = 15;

        private List<dynamic> Results = new List<dynamic>();
        private Action<LogLevel, string> LoggerAction = (level, message) => { };

        public Orchestration(RestfulAPI api, Action<LogLevel, string> loggerAction) {
            this._api = api;
            this.LoggerAction = loggerAction;

            GetOrchestrationSettings();
        }

        private void GetOrchestrationSettings() {
            var settings_record = new RestfulMember(_api.GetMember(OrchestrationEntityName, "z_Settings"));
            if (settings_record != null) {
                var settings = Orchestration.ParseJson(settings_record.Get<string>("Parameters", "{}") as string, "{}");

                var minLogLevelString = (string)Orchestration.GetPropertyValue(settings, "MinLogLevel", "Information");
                Enum.TryParse(minLogLevelString, true, out this.MinLogLevel);
                this.ActivityPollingInterval = (int)Orchestration.GetPropertyValue(settings, "ActivityPollingInterval", 15);
            }

            LoggerAction(LogLevel.Information, $"Orchestration settings: MinLogLevel={this.MinLogLevel}, ActivityPollingInterval={this.ActivityPollingInterval}");
        }

        private List<RestfulMember> GetOrchestrationSteps(string orchestrationCode) {
            var steps = new List<RestfulMember>();
            var options = new RestfulAPI.GetOptions() {
                Filter = $"[{this.OrchestrationEntityName}] eq '{orchestrationCode}'",
                OrderBy = new List<string> { "[StepNumber]" }
            };

            var stepMembers = _api.GetMembers(this.OrchestrationStepEntityName, options);
            foreach (var stepMember in stepMembers)
                steps.Add(new RestfulMember(stepMember));

            return steps;
        }

        private (RestfulMember?, dynamic) GetOrchestration(string orchestrationCode) {
            var member = _api.GetMember(this.OrchestrationEntityName, orchestrationCode);
            if (member != null) {
                var orchestrationMember = new RestfulMember(member);
                var parameters = Orchestration.ParseJson(orchestrationMember.Get<string>("Parameters", "{}"), "{}");
                return (orchestrationMember, parameters);
            }
            return (null, new { });
        }

        public (int, string) Orchestrate(string orchestrationCode) {
            var (orchestrationMember, orchestrationParameters) = GetOrchestration(orchestrationCode);
            if (orchestrationMember == null || orchestrationParameters == null) {
                return (1, $"Orchestration '{orchestrationCode}' not found or has invalid parameters.");
            }

            var threaded = orchestrationMember.Get<string>("Mode", "Sequential") == "Concurrent";
            var abortOnError = orchestrationMember.Get<string>("ErrorHandling", "Abort") == "Abort";

            LogToProfisee(orchestrationCode, null, LogLevel.Information, $"Starting orchestration '{orchestrationCode}' with parameters '{orchestrationMember.Get<string>("Parameters", "")}' running with Threaded({threaded}) and AbortOnError({abortOnError})."); ;

            var threads = new List<Thread>();
            this.Results.Clear();

            foreach (var orchestrationStep in GetOrchestrationSteps(orchestrationCode)) {
                var strategyName = orchestrationStep.Name;
                var stepCode = orchestrationStep.Code;
                var processType = orchestrationStep.Get<string>("ProcessType", "");
                var parameters_json = orchestrationStep.Get<string>("Parameters", "{}");
                var parameters = Orchestration.ParseJson(parameters_json, "{}");

                if (parameters == null)
                    return (1, $"   Orchestration Step '{stepCode}' has invalid parameters.");
                //return new {
                //    Error = true,
                //    Message = $"   Orchestration Step '{stepCode}' has invalid parameters."
                //};
                var enabled = Orchestration.GetPropertyValue(parameters, "Enabled", true) as bool?;
                if (!enabled.HasValue || enabled.Value) {
                    if (threaded) {

                    } else {
                        var runResponse = Run(orchestrationCode, stepCode, strategyName, processType, parameters);

                        if (runResponse.Error && abortOnError) {
                            LogToProfisee(orchestrationCode, stepCode, LogLevel.Error, $"   Aborting orchestration '{orchestrationCode}' due to error in step '{stepCode}'");
                            break;
                        }
                    }
                } else {
                    LogToProfisee(orchestrationCode, stepCode, LogLevel.Warning, $"   Skipping disabled step '{stepCode}' ({strategyName})");
                    continue;
                }

            }

            if (threaded) // Wait for threads to complete...
                foreach (var thread in threads)
                    thread.Join();

            var overallError = false;
            foreach (var result in this.Results)
                if (result.Error)
                    overallError = true;

            if (overallError)
                LogToProfisee(orchestrationCode, null, LogLevel.Error, $"Orchestration '{orchestrationCode}' completed with errors.");
            else
                LogToProfisee(orchestrationCode, null, LogLevel.Information, $"Orchestration '{orchestrationCode}' completed successfully.");

            return (overallError ? 0 : 1, $"Orchestration '{orchestrationCode}' completed {(overallError ? "with errors" : "successfully")}.");
        }

        private dynamic? Run(string orchestrationCode, string stepCode, string strategyName, string processType, dynamic parameters) {
            return FunctionWrapper($"Run({orchestrationCode}, {stepCode}, {strategyName}, {processType}, {JsonConvert.SerializeObject(parameters)})",
                orchestrationCode, stepCode, () => {
                    var since_date_time = DateTime.UtcNow;
                    var runErrored = false;

                    var startProcessResult = StartProcess(orchestrationCode, stepCode, strategyName, processType, parameters);

                    if (!startProcessResult.Error) {
                        var waitForComplettionResult = WaitForCompletion(orchestrationCode, stepCode, strategyName, processType, parameters, since_date_time);

                        if (waitForComplettionResult.Error)
                            runErrored = true;
                    } else {
                        runErrored = true;
                    }

                    var result = new {
                        Orchestration = orchestrationCode,
                        OrchestrationStep = stepCode,
                        Name = strategyName,
                        ProcessType = processType,
                        Parameters = parameters,
                        Error = runErrored,
                        Message = $"Running {processType} with parameters {parameters}"
                    };
                    this.Results.Add(result);
                    return result;
                });
        }

        private dynamic? StartProcess(string orchestrationCode, string stepCode, string strategyName, string processType, dynamic parameters) {
            return FunctionWrapper($"StartProcess({orchestrationCode}, {stepCode}, {strategyName}, {processType}, {JsonConvert.SerializeObject(parameters)})",
                orchestrationCode, stepCode, () => {
                    switch (processType.ToLower()) {
                        case "connect":
                            return StartProcessConnect(orchestrationCode, stepCode, strategyName, processType, parameters);
                        case "matching":
                            return StartProcessMatching(orchestrationCode, stepCode, strategyName, processType, parameters);
                    }

                    return new {
                        Error = true,
                        Message = $"Unknown ProcessType '{processType}' for orchestration '{orchestrationCode}'."
                    };
                });
        }

        private dynamic? StartProcessConnect(string orchestrationCode, string stepCode, string strategyName, string processType, dynamic parameters) {
            return FunctionWrapper($"StartProcessConnect({orchestrationCode}, {stepCode}, {strategyName}, {processType}, {JsonConvert.SerializeObject(parameters)})",
                orchestrationCode, stepCode, () => {
                    if (this.WhatIf) {
                        LogToProfisee(orchestrationCode, stepCode, LogLevel.Information, $"   WhatIf: Starting Connect process '{strategyName}' with parameters '{parameters}'");
                        return (dynamic)new {
                            Error = false,
                            Message = $"   WhatIf: Started Connect process '{strategyName}' with parameters '{parameters}'"
                        };
                    }

                    string? filter = Orchestration.GetPropertyValue(parameters, "Filter", null);
                    var response = _api.RunConnectBatch(strategyName, filter);

                    if (_api.StatusCode != System.Net.HttpStatusCode.OK)
                        LogToProfisee(orchestrationCode, stepCode, LogLevel.Error, $"   Error starting Connect process '{strategyName}'. StatusCode={_api.StatusCode}, Response={response}");

                    return (dynamic)new {
                        Error = _api.StatusCode != System.Net.HttpStatusCode.OK,
                        Response = response
                    };
                });
        }

        private dynamic? StartProcessMatching(string orchestrationCode, string stepCode, string strategyName, string processType, dynamic parameters) {
            return FunctionWrapper($"StartProcessMatching({orchestrationCode}, {stepCode}, {strategyName}, {processType}, {JsonConvert.SerializeObject(parameters)})",
                orchestrationCode, stepCode, () => {


                    if (this.WhatIf) {
                        LogToProfisee(orchestrationCode, stepCode, LogLevel.Information, $"   WhatIf: Starting Matching process '{strategyName}' with parameters '{parameters}'");
                        return new {
                            Error = false,
                            Message = $"   WhatIf: Started Matching process '{strategyName}' with parameters '{parameters}'"
                        };
                    }

                    var processActionString = Orchestration.GetPropertyValue(parameters, "ProcessAction", "MatchingOnly");
                    var processAction = ProcessAction.MatchingOnly;
                    Enum.TryParse(processActionString, true, out processAction);
                    var response = _api.ProcessMatchingActions(strategyName, processAction);

                    if (_api.StatusCode != System.Net.HttpStatusCode.OK)
                        LogToProfisee(orchestrationCode, stepCode, LogLevel.Error, $"   Error starting Matching process '{strategyName}'. StatusCode={_api.StatusCode}, Response={response}");

                    return new {
                        Error = _api.StatusCode != System.Net.HttpStatusCode.OK,
                        Response = response
                    };
                });
        }

        private string? GetActivityForProcessType(string ProcessType, dynamic parameters) {
            switch (ProcessType.ToLower()) {
                case "connect":
                    return Orchestration.GetPropertyValue(parameters, "ActivityType", "Connect Strategy Execution") as string;
                case "matching":
                    return Orchestration.GetPropertyValue(parameters, "ActivityType", "Clustering & Survivorship") as string;
            }
            return null;
        }

        private dynamic? WaitForCompletion(string orchestrationCode, string stepCode, string strategyName, string processType, dynamic parameters, DateTime sinceDateTime) {
            return FunctionWrapper($"WaitForCompletion({orchestrationCode}, {stepCode}, {strategyName}, {processType}, {JsonConvert.SerializeObject(parameters)}, {sinceDateTime})",
                orchestrationCode, stepCode, () => {
                    if (this.WhatIf) {
                        LogToProfisee(orchestrationCode, stepCode, LogLevel.Information, $"   WhatIf: Waiting for completion of {processType} '{strategyName}' with parameters '{parameters}'");
                        return new {
                            FirstActivityDateTime = DateTime.Now,
                            ElapsedTime = DateTime.Now - DateTime.Now,
                            Error = false,
                            Activities = new List<dynamic>()
                        };
                    }

                    var firstActivityDateTime = (DateTime?)null;
                    var wasSuccessful = false;
                    var filteredMonitorActivities = new List<dynamic>();

                    var getOptions = new RestfulAPI.GetOptions() {
                        // Filter = $"contains([Name], '{strategyName}') and [ActivityType] eq '{GetActivityForProcessType(processType, parameters)}' and [Service] eq '{processType}' and [StartedTime] gt {sinceDateTime.ToString("%Y-%m-%dT%H:%M:%SZ")}"
                        Filter = $"[ActivityType] eq '{GetActivityForProcessType(processType, parameters)}' and [Service] eq '{processType}' and [StartedTime] gt {sinceDateTime.ToString("yyyy-MM-ddThh:mm:ssZ")}"
                    };

                    while (true) {
                        var monitorActivities = this._api.GetMonitorActivities(getOptions);

                        filteredMonitorActivities.Clear();
                        if (monitorActivities != null)
                            foreach (var activity in monitorActivities) {
                                var name = (string)Orchestration.GetPropertyValue(activity, "Name", "");
                                if (name.Contains(strategyName, StringComparison.InvariantCultureIgnoreCase))
                                    filteredMonitorActivities.Add(activity);
                            }

                        if (filteredMonitorActivities.Count > 0) {
                            if (firstActivityDateTime == null)
                                firstActivityDateTime = DateTime.Now;

                            var numberOfNotRunning = 0;
                            var numberOfSucceeded = 0;

                            foreach (var activity in filteredMonitorActivities) {
                                var status = (string)Orchestration.GetPropertyValue(activity, "Status", "Unknown");

                                if (!status.Equals("Running", StringComparison.InvariantCultureIgnoreCase))
                                    numberOfNotRunning += 1;

                                if (status.Equals("Succeeded", StringComparison.InvariantCultureIgnoreCase))
                                    numberOfSucceeded += 1;
                            }

                            if (numberOfNotRunning == filteredMonitorActivities.Count) {
                                if (numberOfSucceeded == filteredMonitorActivities.Count)
                                    wasSuccessful = true;
                                break;
                            }
                        }

                        Thread.Sleep(this.ActivityPollingInterval * 1000);
                    }

                    return new {
                        FirstActivityDateTime = firstActivityDateTime,
                        ElapsedTime = (DateTime.Now - firstActivityDateTime),
                        Error = !wasSuccessful,
                        Activities = filteredMonitorActivities
                    };
                });
        }

        private bool ShouldLog(LogLevel level) {
            return level >= this.MinLogLevel;
        }

        private void LogToProfisee(string orchestrationCode, string? stepCode, LogLevel level, string message) {
            if (!ShouldLog(level))
                return;

            LoggerAction(level, message);

            this._api.MergeMember(this.OrchestrationLogEntityName, new RestfulMember(new Dictionary<string, object> {
                { this.OrchestrationEntityName, orchestrationCode },
                { this.OrchestrationStepEntityName, stepCode },
                { "LogLevel", level.ToString() },
                { "Message", message }
            }).Member);
        }

        private dynamic? FunctionWrapper(string functionName, string orchestrationCode, string stepCode, Func<dynamic?> func) {
            try {
                LogToProfisee(orchestrationCode, stepCode, LogLevel.Debug, $"Entering {functionName}");
                var result = func();
                var resultAsJson = JsonConvert.SerializeObject(result);
                LogToProfisee(orchestrationCode, stepCode, LogLevel.Debug, $"Exiting {functionName} => {resultAsJson}");

                return result;
            } catch (Exception ex) {
                LogToProfisee(orchestrationCode, stepCode, LogLevel.Error, $"Exception in {functionName}: {ex.Message}\n{ex.StackTrace}");
                return (dynamic)new {
                    Error = true,
                    Message = $"Exception in {functionName}: {ex.Message}\n{ex.StackTrace}"
                };
            }
        }

        public static dynamic ParseJson(string json, string defaultJson) {
            try {
                return JsonConvert.DeserializeObject<dynamic>(json);
            } catch (Exception) {
                if (!string.IsNullOrEmpty(defaultJson))
                    return ParseJson(defaultJson, string.Empty);

                return JsonConvert.DeserializeObject<dynamic>("{}");
            }
        }

        public static object GetPropertyValue(dynamic obj, string name, object defaultValue) {
            foreach (var prop in obj.Children()) {
                if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase))
                    return prop.Value.Value; // Weird that we have to get the value of the value...
            }
            return defaultValue;
        }
    }
}
