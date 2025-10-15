using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RestSharp;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.Metrics;
using System.Linq;
using System.Net;
using System.Reflection;
using System.Reflection.Emit;
using System.Text;
using System.Threading.Tasks;
using System.Web;
using static Profisee.MDM.RestfulAPI;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace Profisee.MDM {
    public enum ProcessAction {
        MatchingOnly = 0,
        MatchingAndSurvivorship = 1,
        SurvivorshipOnly = 2,
        ClearPriorResults = 3,
        ClearAllPriorResults = 4
    }
    public enum RequestOperation {
        Get,
        Put,
        Post,
        Patch,
        Delete
    }
    public class RestfulAPI {
        //private readonly ILogger<CreateCloudEventFunction> Logger;

        private readonly Action<LogLevel, string> LoggerAction;

        private string ProfiseeUrl;
        private string ClientId;
        public dynamic LastResponse { get; set; }
        public HttpStatusCode StatusCode { get; set; }
        public dynamic? Errors { get; set; }
        public bool SuccessStatusCode { get { return ((int)StatusCode >= 200) && ((int)StatusCode < 300); } }

        public RestfulAPI(string url, string clientId, Action<LogLevel, string> loggerAction) { // ILogger<CreateCloudEventFunction> logger) {
            ProfiseeUrl = url;
            ClientId = clientId;
            //Logger = logger;
            LoggerAction = loggerAction;
            LastResponse = new JObject();
            SetResponseHandlers();
        }
        private Dictionary<(string, HttpStatusCode), Func<RestResponse, dynamic?>> ResponseHandlers;

        private void SetResponseHandlers() {
            ResponseHandlers = new Dictionary<(string, HttpStatusCode), Func<RestResponse, dynamic?>> {
                { ("UnmatchRecords",  HttpStatusCode.NoContent), (response) => { return SuccessHandler(response, "Success - records unmatched."); } },
                { ("UpdateMatchingStrategy",  HttpStatusCode.NoContent), (response) => { return SuccessHandler(response, "Success - Successfully updated the continuous matching setting of the matching strategy."); } },

                { (string.Empty,  HttpStatusCode.OK), (response) => { return SuccessDataHandler(response); } },
                { (string.Empty,  HttpStatusCode.Created), (response) => { return SuccessDataHandler(response); } },
                { (string.Empty,  HttpStatusCode.NoContent), (response) => { return SuccessDataHandler(response); } },
                { (string.Empty,  HttpStatusCode.MultiStatus), (response) => { return SuccessDataHandler(response); } },

                { (string.Empty,  HttpStatusCode.BadRequest), (response) => { return ErrorHandler(response, "Bad Request - One or more validation errors occurred."); } },
                { (string.Empty,  HttpStatusCode.Unauthorized), (response) => { return ErrorHandler(response, "Not Authorized - You are not authorized to access this resource."); } },
                { (string.Empty,  HttpStatusCode.NotFound), (response) => { return ErrorHandler(response, "Not Found - The requested entity could not be found."); } },
                { (string.Empty,  HttpStatusCode.InternalServerError), (response) => { return ErrorHandler(response, "Internal Server Error - An unexpected error occurred on the server. Please check your Profisee logs for more details."); } }
            };
        }

        private RestClient GetRestClient() {
            var client = new RestClient(ProfiseeUrl);
            client.AddDefaultHeader("x-api-key", ClientId);
            return client;
        }

        private dynamic? CheckResponse(string functionName, RestResponse response) {
            this.LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content); ;
            this.StatusCode = response.StatusCode;

            var handler = ResponseHandlers.FirstOrDefault(h => (h.Key.Item1 == functionName || string.IsNullOrEmpty(h.Key.Item1)) && h.Key.Item2 == response.StatusCode).Value;

            if (handler != null)
                return handler(response);

            return new {
                this.StatusCode,
                Message = $"ResponseHandler not found for ('{functionName}', {this.StatusCode}).",
            };
        }

        private dynamic? SuccessHandler(RestResponse response, string message) {
            this.Errors = new { };
            return new {
                this.StatusCode,
                Message = message
            };
        }
        private dynamic? SuccessDataHandler(RestResponse response) {
            this.Errors = GetPropertyValue(this.LastResponse, "errors");
            var data = GetPropertyValue(this.LastResponse, "data");
            if (data != null) return data;
            return this.LastResponse;
        }
        private dynamic? ErrorHandler(RestResponse response, string message) {
            this.Errors = this.LastResponse;
            return new {
                this.StatusCode,
                Message = message,
                this.Errors
            };
        }

        private dynamic? CallAPI(Method requestMethod, string url, dynamic? body = null) {
            // Get the Function that called this for the RequestHandler mapping...
            StackTrace stackTrace = new System.Diagnostics.StackTrace();
            StackFrame frame = stackTrace.GetFrames()[1];
            MethodInfo method = (MethodInfo)frame.GetMethod();
            string methodName = method.Name;

            var request = new RestRequest($"{this.ProfiseeUrl}/{url}", requestMethod);

            if (body != null) {
                var bodyAsString = Newtonsoft.Json.JsonConvert.SerializeObject(body);
                RestSharp.RestRequestExtensions.AddStringBody((RestRequest)request, bodyAsString, DataFormat.Json);
            }

            RestResponse response = null;

            var restClient = GetRestClient();

            try {
                switch (requestMethod) {
                    case Method.Get:
                        response = restClient.Get(request);
                        break;
                    case Method.Patch:
                        response = restClient.Patch(request);
                        break;
                    case Method.Post:
                        response = DoIt(request).GetAwaiter().GetResult();
                        break;
                    case Method.Delete:
                        response = restClient.Delete(request);
                        break;
                }
            } catch (HttpRequestException httpRequestException) {
                
            }
            return CheckResponse(methodName, response);
        }

        private async Task<RestResponse> DoIt(RestRequest request) {
            return await GetRestClient().ExecuteAsync(request);
        }

        private void ChangeAttributeName() {

        }

        // ============================================================================================
        // New methods to be migrated to CallAPI
        // ============================================================================================

        // ============================================================================================
        // AddressVerification
        // ============================================================================================
        public dynamic? GetAddressVerificationStrategies() {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies"),
                (exception) => ExceptionHandler(exception));
        }
        public dynamic? GetAddressVerificationStrategy(string strategyName) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies/{strategyName}"),
                (exception) => ExceptionHandler(exception));
        }
        public dynamic? GetAddressVerificationStrategyAttributes(string strategyName, string recordCode) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName, recordCode },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies/{strategyName}/address?recordCode={recordCode}"),
                (exception) => ExceptionHandler(exception));
        }
        public dynamic? StartAddressVerificationStrategy(string strategyName, dynamic? body) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies/{strategyName}/job", body),
                (exception) => ExceptionHandler(exception));
        }
        //public dynamic? StopAddressVerificationStrategy(string strategyName) {
        //    return RestfulAPI.FunctionWrapper<dynamic?>(
        //        new { strategyName },
        //        LoggerAction,
        //        () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies/{strategyName}/job/cancel"),
        //        (exception) => ExceptionHandler(exception));
        //}
        public dynamic? StopAddressVerificationStrategy(string strategyName) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/AddressVerificationStrategies/{strategyName}/job/cancel"),
                (exception) => ExceptionHandler(exception));
        }
        /*
    def StartAddressVerificationStrategy(self, strategyName, records) :
        return self.CallAPI(RequestOperation.Post, f"rest/v1/AddressVerificationStrategies/{strategyName}/records", json = records)
        */

        // ============================================================================================
        // Attributes
        // ============================================================================================

        public dynamic? GetAttributes(string entityName = "") {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { entityName },
                LoggerAction,
                () => {
                    if (string.IsNullOrEmpty(entityName))
                        return CallAPI(Method.Get, $"rest/v1/Attributes");
                    else
                        return CallAPI(Method.Get, $"rest/v1/Entities/{entityName}/attributes");
                },
                (exception) => ExceptionHandler(exception));
        }

        // ============================================================================================
        // Connect
        // ============================================================================================

        public dynamic? RunConnectBatch(string strategyName, string? filter = null, List<string>? recordCodes = null) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName, filter, recordCodes },
                LoggerAction,
                () => {
                    if (recordCodes == null) recordCodes = new List<string>();
                    var body = new {
                        FilterExpression = filter != null ? filter : "",
                        Codes = recordCodes
                    };                    
                    return CallAPI(Method.Post, $"/rest/v1/Connect/strategies/{strategyName}/Batch", body);
                },
                (exception) => ExceptionHandler(exception));




            //LoggerAction(LogLevel.Information, $"RunConnectBatch({strategyName}, {filter}, {string.Join(',', recordCodes)})");

            //return Wrappers.WrapWithTryCatch("RunConnectBatch", LoggerAction, () => {
            //    var response = PostRequest($"/rest/v1/Connect/strategies/{strategyName}/Batch", body);
            //    LastResponse = JsonConvert.DeserializeObject<dynamic>(value: response.Content);
            //    DumpProfiseeErrors();
            //    return LastResponse;
            //});
        }

        // ============================================================================================
        // Matching
        // ============================================================================================

        public dynamic? ProcessMatchingActions(string strategyName, ProcessAction processAction = ProcessAction.MatchingOnly) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { strategyName, processAction },
                LoggerAction,
                () => {
                    var actions = new List<string>();
                    switch (processAction) {
                        case ProcessAction.MatchingAndSurvivorship: actions.Add("IncludeSurvivorship"); break;
                        case ProcessAction.SurvivorshipOnly: actions.Add("SurvivorshipOnly"); break;
                        case ProcessAction.ClearPriorResults: actions.Add("ClearPriorResults"); actions.Add("ClearMatchingResults"); break;
                        case ProcessAction.ClearAllPriorResults: actions.Add("ClearAllPriorResults"); actions.Add("ClearMatchingResults"); break;
                    }
                    var body = new {
                        Actions = actions
                    };
                    return CallAPI(Method.Post, $"/rest/v1/Matching/{strategyName}/processActions", body);
                },
                (exception) => ExceptionHandler(exception));



            //return Wrappers.WrapWithTryCatch("ProcessMatchingActions", LoggerAction, () => {
            //    var response = PostRequest($"/rest/v1/Matching/{strategyName}/processActions", body);
            //    LastResponse = JsonConvert.DeserializeObject<dynamic>(value: response.Content);
            //    DumpProfiseeErrors();
            //    return LastResponse;
            //});
        }

        // ============================================================================================
        // Monitor
        // ============================================================================================

        public dynamic? GetMonitorActivities(GetOptions getOptions = null) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { getOptions },
                LoggerAction,
                () => {
                    if (getOptions == null) {
                        getOptions = new GetOptions();
                        getOptions.OrderBy.Add("[StartedTime] desc");
                    }
                    return CallAPI(Method.Get, $"rest/v1/Monitor/activities?{getOptions.QueryString()}");
                },
                (exception) => ExceptionHandler(exception));
        }

        // ============================================================================================
        // Records
        // ============================================================================================
        public dynamic? GetRecord(string entityName, string memberCode) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { entityName, memberCode },
                LoggerAction,
                () => {
                    var members = GetRecords(entityName, new GetOptions($"[Code] eq '{memberCode}'"));
                    if (members.Count > 0) return members[0];
                    return null;
                },
                (exception) => ExceptionHandler(exception));
        }

        public dynamic? GetRecords(string entityName, GetOptions getOptions) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { entityName, getOptions },
                LoggerAction,
                () => CallAPI(Method.Get, $"rest/v1/records/{entityName}?{getOptions.QueryString()}"),
                (exception) => ExceptionHandler(exception));
        }

        public dynamic? MergeRecord(string entityName, dynamic member) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { entityName, member },
                LoggerAction,
                () => MergeRecords(entityName, new List<dynamic> { member }),
                (exception) => ExceptionHandler(exception));
            // return MergeRecords(entityName, new List<dynamic> { member });
        }

        public dynamic? MergeRecords(string entityName, List<dynamic> members) {
            return RestfulAPI.FunctionWrapper<dynamic?>(
                new { entityName, members },
                LoggerAction,
                () => CallAPI(Method.Patch, $"rest/v1/records/{entityName}", members),
                (exception) => ExceptionHandler(exception));
            // return CallAPI(Method.Patch, $"rest/v1/records/{entityName}", members);
        }

        // ============================================================================================
        // Old methods to be migrated to CallAPI
        // ============================================================================================
        private void SetStatusCode(RestResponse response) {
            LoggerAction(LogLevel.Debug, $"   StatusCode = {response.StatusCode}");
            LoggerAction(LogLevel.Debug, $"   LastResponse = {response.Content}");
            this.StatusCode = response.StatusCode;
        }
        private RestResponse GetResponse(string url) {
            LoggerAction(LogLevel.Debug, $"   GetResponse(\"{url}\")");
            //Logger.LogDebug($"   GetResponse(\"{url}\")");
            var request = new RestRequest(url, Method.Get);
            var response = GetRestClient().Get(request);
            SetStatusCode(response);
            return response;
        }
        private RestResponse PatchResponse(string url, dynamic body) { // JArray bodyArray) {
            LoggerAction(LogLevel.Debug, $"   PatchResponse(\"{url}\")");

            //var index = 0;
            //foreach (var data in bodyArray) {
            //    var dataAsString = data.ToString().Replace(Environment.NewLine, "");
            //    LoggerAction(LogLevel.Debug, $"   body[{index}] = '{dataAsString}'");
            //    index += 1;
            //}
            var bodyAsString = Newtonsoft.Json.JsonConvert.SerializeObject(body);
            LoggerAction(LogLevel.Debug, $"   body = '{bodyAsString}'");

            var request = new RestRequest(url, Method.Patch);
            // Fix: Cast request to RestRequest to avoid dynamic dispatch for extension method
            RestSharp.RestRequestExtensions.AddStringBody((RestRequest)request, bodyAsString, DataFormat.Json);
            var response = GetRestClient().Patch(request);
            SetStatusCode(response);
            return response;
        }
        private RestResponse PostRequest(string url, dynamic body) {
            LoggerAction(LogLevel.Debug, $"   PostResponse(\"{url}\")");

            var bodyAsString = Newtonsoft.Json.JsonConvert.SerializeObject(body);
            LoggerAction(LogLevel.Debug, $"   body = '{bodyAsString}'");

            var request = new RestRequest(url, Method.Post);
            // Fix: Cast request to RestRequest to avoid dynamic dispatch for extension method
            RestSharp.RestRequestExtensions.AddStringBody((RestRequest)request, bodyAsString, DataFormat.Json);
            var response = GetRestClient().Post(request);
            SetStatusCode(response);
            return response;
        }
        private RestResponse DeleteResponse(string url) {
            LoggerAction(LogLevel.Debug, $"   DeleteResponse(\"{url}\"");
            var request = new RestRequest(url, Method.Delete);
            var response = GetRestClient().Delete(request);
            SetStatusCode(response);
            return response;
        }
        private void DumpProfiseeErrors() {
            if ((LastResponse != null) && (LastResponse?.errors != null) && ((JContainer)LastResponse.errors).Count > 0)
                LoggerAction(LogLevel.Debug, $"   Errors: {LastResponse?.errors.ToString()}");
        }
        private void DumpProfiseeData() {
            var index = 0;
            foreach (var data in LastResponse.data) {
                var dataAsString = data.ToString().Replace(Environment.NewLine, "");
                LoggerAction(LogLevel.Debug, $"   data[{index}] = '{dataAsString}'");
                index += 1;
            }
        }

        public dynamic GetMemberURL(string entityName, string code) {
            LoggerAction(LogLevel.Information, $"GetMember({entityName}, {code})");

            return Wrappers.WrapWithTryCatch<dynamic>("GetMember", LoggerAction, () => {
                var response = GetResponse($"/rest/v1/records/{entityName}/{code}");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                DumpProfiseeData();
                if (LastResponse.resultCount == 1) return LastResponse.data[0];
                return null;
            });
        }

        public dynamic GetMember(string entityName, string code) {
            LoggerAction(LogLevel.Information, $"GetMember({entityName}, {code})");

            return Wrappers.WrapWithTryCatch<dynamic>("GetMember", LoggerAction, () => {
                var members = GetMembers(entityName, new GetOptions($"[Code] eq '{code}'"));
                if (members.Count > 0) return members[0];
                return null;
            });
        }

        public dynamic GetTransactions(string entityName, string memberCode) {
            LoggerAction(LogLevel.Information, $"GetTransactions({entityName}, {memberCode})");

            return Wrappers.WrapWithTryCatch<dynamic>("GetTransactions", LoggerAction, () => {
                var response = GetResponse($"/rest/v1/transactions/{entityName}?PageNumber=1&PageSize=50&recordCode={memberCode}");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                DumpProfiseeData();
                return LastResponse.data;
            });
        }

        public dynamic GetMembers(string entityName, GetOptions getOptions) {
            LoggerAction(LogLevel.Information, $"GetMembers({entityName}, {getOptions.QueryString()})");

            return Wrappers.WrapWithTryCatch("GetMembers", LoggerAction, () => {
                var response = GetResponse($"/rest/v1/records/{entityName}?{getOptions.QueryString()}");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                DumpProfiseeData();
                return LastResponse.data;
            });
        }
        public dynamic MergeMember(string entityName, dynamic member, bool autoAddAllDbas = false) {
            return MergeMembers(entityName, new List<dynamic> { member }, autoAddAllDbas);
        }

        public dynamic MergeMembers(string entityName, List<dynamic> members, bool autoAddAllDbas = false) {
            LoggerAction(LogLevel.Information, $"MergeMember({entityName})");

            //return Wrappers.WrapWithTryCatch("MergeMember", LoggerAction, () => {
            try {
                //var bodyArray = new JArray();
                //foreach (var member in members)
                //    bodyArray.Add(member);

                var mergeOptions = string.Empty;
                if (autoAddAllDbas) mergeOptions = "?autoAddAllDbas=true";

                var response = PatchResponse($"/rest/v1/records/{entityName}{mergeOptions}", members);
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                return LastResponse;
            } catch (Exception exception) {
                Debug.WriteLine($"Exception: {exception.Message}");
            }
            //});
            return null;
        }

        public dynamic DeleteMember(string entityName, string code) {
            return DeleteMembers(entityName, new List<string> { code });
        }

        public dynamic? DeleteMembers(string entityName, List<string> codes) {
            LoggerAction(LogLevel.Information, $"DeleteMembers({entityName}, {string.Join(",", codes)})");

            return Wrappers.WrapWithTryCatch("DeleteMembers", LoggerAction, () => {
                var response = DeleteResponse($"/rest/v1/records/{entityName}?RecordCodes={string.Join(",", codes)}");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                return LastResponse;
            });
        }

        public dynamic? GetEntities() {
            LoggerAction(LogLevel.Information, $"GetEntities()");

            return Wrappers.WrapWithTryCatch("GetEntities", LoggerAction, () => {
                var response = GetResponse($"/rest/v1/entities");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                return LastResponse;
            });
        }





        public static object? GetPropertyValue(dynamic obj, string name, object? defaultValue = null) {
            foreach (var prop in obj.Children()) {
                if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase)) {
                    if (prop.Value.GetType().Name.Equals("JArray")) return prop.Value;
                    return prop.Value.Value; // Otherwise is a JToken and we need to get the value of the value...
                }
            }
            return defaultValue;
        }

        public static void SetPropertyValue(dynamic obj, string name, object value) {


            foreach (var prop in obj.Children()) {
                if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase)) {
                    prop.Value = JToken.FromObject(value);
                    return;
                }
            }
            if (value == null) return;
            // If we get here property was not in the member yet...
            obj[name] = JToken.FromObject(value);
        }
        private dynamic? ExceptionHandler(Exception exception) {
            return new {
                Error = true,
                Message = $"Exception: {exception.Message}\n{exception.StackTrace}"
            };
        }
        static public T? FunctionWrapper<T>(dynamic parameters, Action<LogLevel, string> loggerAction, Func<T> func, Func<Exception, T> exceptionFunc) {
            var functionCallAsString = "Unknown()";
            try {
                var frames = new StackTrace().GetFrames();
                MethodInfo? method = frames != null && frames.Length > 1 ? frames[1].GetMethod() as MethodInfo : null;
                var parameterValues = new List<string>();

                if (method != null) {
                    foreach (var parameterInfo in method.GetParameters()) {
                        var argValue = parameters.GetType().GetProperty(parameterInfo.Name)?.GetValue(parameters, null);
                        parameterValues.Add($"{parameterInfo.Name}: {argValue}");
                    }
                    functionCallAsString = $"{method.DeclaringType}.{method.Name}({string.Join(", ", parameterValues)})";
                }
                loggerAction(LogLevel.Trace, $"Enter {functionCallAsString} :");

                var returnValue = func();

                loggerAction(LogLevel.Trace, $"Exit  {functionCallAsString} => {returnValue}");

                return returnValue;
            }  catch (Exception exception) {
                loggerAction(LogLevel.Error, $"Error {functionCallAsString} : \n      Exception {exception.Message}\n{exception.StackTrace}");
                return exceptionFunc(exception);
            }
        }

        public class GetOptions {
            public GetOptions(string filter = "") { Filter = filter; }
            public string Filter { get; set; }
            public List<string> OrderBy { get; set; } = new List<string>();
            public List<string> Attributes { get; set; } = new List<string>();
            public enum DbaFormatType { Default = 0, CodeOnly = 1, CodeAndName = 2 }
            public DbaFormatType DbaFormat { get; set; } = DbaFormatType.Default;
            public bool CountsOnly { get; set; } = false;
            public int PageNumber { get; set; } = 1;
            public int PageSize { get; set; } = 50;

            public string QueryString() {
                var queryString = System.Web.HttpUtility.ParseQueryString(string.Empty);

                if (!string.IsNullOrEmpty(this.Filter))
                    queryString.Add("filter", this.Filter); // HttpUtility.UrlEncode(this.Filter));
                if (this.OrderBy.Count > 0)
                    queryString.Add("orderby", string.Join(",", this.OrderBy));
                if (this.Attributes.Count > 0)
                    queryString.Add("attributes", string.Join(",", this.Attributes));
                if (this.CountsOnly)
                    queryString.Add("countsonly", "true");
                if (this.DbaFormat != DbaFormatType.Default)
                    queryString.Add("dbaformat", ((int)this.DbaFormat).ToString());
                if (this.PageNumber != 1)
                    queryString.Add("pagenumber", this.PageNumber.ToString());
                if (this.PageSize != 50)
                    queryString.Add("pagesize", this.PageSize.ToString());

                return queryString.ToString();
            }

            public override string ToString() {
                return HttpUtility.UrlDecode(QueryString());
            }
        }
    }
}