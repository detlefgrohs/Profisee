using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RestSharp;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace Common {
    public class RestfulAPI {
        //private readonly ILogger<CreateCloudEventFunction> Logger;

        private readonly Action<LogLevel, string> LoggerAction;

        private string ProfiseeUrl;
        private string ClientId;
        public dynamic LastResponse { get; set; }

        public RestfulAPI(string url, string clientId, Action<LogLevel, string> loggerAction) { // ILogger<CreateCloudEventFunction> logger) {
            ProfiseeUrl = url;
            ClientId = clientId;
            //Logger = logger;
            LoggerAction = loggerAction;
            LastResponse = new JObject();
        }
        private RestClient GetRestClient() {
            var client = new RestClient(ProfiseeUrl);
            client.AddDefaultHeader("x-api-key", ClientId);
            return client;
        }
        private RestResponse GetResponse(string url) {
            LoggerAction(LogLevel.Debug, $"   GetResponse(\"{url}\")");
            //Logger.LogDebug($"   GetResponse(\"{url}\")");
            var request = new RestRequest(url, Method.Get);
            var response = GetRestClient().Get(request);
            LoggerAction(LogLevel.Debug, $"   LastResponse = {response.Content}");
            //Logger.LogDebug($"   LastResponse = {response.Content}");
            return response;
        }
        private RestResponse MergeResponse(string url, JArray bodyArray) {
            LoggerAction(LogLevel.Debug, $"   MergeResponse(\"{url}\")");

            var index = 0;
            foreach (var data in bodyArray) {
                var dataAsString = data.ToString().Replace(Environment.NewLine, "");
                LoggerAction(LogLevel.Debug, $"   body[{index}] = '{dataAsString}'");
                index += 1;
            }

            var request = new RestRequest(url, Method.Patch);
            request.AddStringBody(bodyArray.ToString(), DataFormat.Json);
            var response = GetRestClient().Patch(request);
            LoggerAction(LogLevel.Debug, $"   LastResponse = {response.Content}");
            return response;
        }
        private RestResponse DeleteResponse(string url) {
            LoggerAction(LogLevel.Debug, $"   DeleteResponse(\"{url}\"");
            var request = new RestRequest(url, Method.Delete);
            var response = GetRestClient().Delete(request);
            LoggerAction(LogLevel.Debug, $"   LastResponse = {response.Content}");
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
                var bodyArray = new JArray();
                foreach (var member in members)
                    bodyArray.Add(member);

                var mergeOptions = string.Empty;
                if (autoAddAllDbas) mergeOptions = "?autoAddAllDbas=true";

                var response = MergeResponse($"/rest/v1/records/{entityName}{mergeOptions}", bodyArray);
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

        public dynamic DeleteMembers(string entityName, List<string> codes) {
            LoggerAction(LogLevel.Information, $"DeleteMembers({entityName}, {string.Join(",", codes)})");

            return Wrappers.WrapWithTryCatch("DeleteMembers", LoggerAction, () => {
                var response = DeleteResponse($"/rest/v1/records/{entityName}?RecordCodes={string.Join(",", codes)}");
                LastResponse = JsonConvert.DeserializeObject<dynamic>(response.Content);
                DumpProfiseeErrors();
                return LastResponse;
            });
        }

        public static object GetPropertyValue(dynamic obj, string name) {
            foreach (var prop in obj.Children()) {
                if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase))
                    return prop.Value.Value; // Weird that we have to get the value of the value...
            }
            return null;
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
                    queryString.Add("filter", this.Filter);
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
        }
    }
}