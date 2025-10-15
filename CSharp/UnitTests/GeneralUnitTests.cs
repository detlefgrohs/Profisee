using FluentAssertions;
using Microsoft.VisualStudio.TestPlatform.CommunicationUtilities;
using Profisee.MDM;
using RestSharp;
using System.Diagnostics;
using System.Net;
using System.Net.WebSockets;
using System.Reflection;


namespace Profisee.MDM.UnitTests {
    [TestClass]
    public sealed class GeneralUnitTests {
        [TestMethod]
        public void DynamicPrinting() {
            var result = new {
                Name = "Test",
                Value = 123,
                Active = true
            };

            dynamic result_as_dynamic = (dynamic)result;

            Debug.WriteLine(result);
            //Debug.WriteLine(result_as_dynamic);

            var result_as_string = result.ToString();
            var result_as_dynamic_string = result_as_dynamic.ToString();


            var body = new {
                FilterExpression = "",
                Codes = new List<string>()
            };

            var body_as_string = body.ToString();

            var body_as_json = Newtonsoft.Json.JsonConvert.SerializeObject(body);


        }
        [TestMethod]
        public void GetCallerNameTest() {
            var callerName = Callee();
        }

        public string Callee() {
            StackTrace stackTrace = new System.Diagnostics.StackTrace();
            StackFrame frame = stackTrace.GetFrames()[1];
            MethodInfo method = (MethodInfo)frame.GetMethod();
            string methodName = method.Name;
            Type methodsClass = method.DeclaringType;
            return methodName;
        }


        [TestMethod]
        public void FunctionWrapperTest() {
            var response = WrapperCaller("test", 123, new { Name = "Test" });
        }

        public dynamic? WrapperCaller(string arg1, int arg2, dynamic body) {
            return FunctionWrapper<dynamic?>(new { arg1, arg2, body }, () => {
                Debug.WriteLine("Inside the function");
                throw new NotImplementedException("Dude not yet!");
                return new {
                    Message = "Hello World"
                };
            });
        }

        static public T FunctionWrapper<T>(dynamic parameters, Func<T> func) {
            var functionCallAsString = "Unknown()";
            try {
                MethodInfo method = (MethodInfo)(new System.Diagnostics.StackTrace().GetFrames()[1]).GetMethod();
                var parameterValues = new List<string>();

                foreach (var parameterInfo in method.GetParameters()) {
                    var argValue = parameters.GetType().GetProperty(parameterInfo.Name)?.GetValue(parameters, null);
                    parameterValues.Add($"{parameterInfo.Name}: {argValue}");
                }

                functionCallAsString = $"{method.DeclaringType}.{method.Name}({string.Join(", ", parameterValues)})";
                Debug.WriteLine($"Enter {functionCallAsString} :");

                var returnValue = func();

                Debug.WriteLine($"Exit  {functionCallAsString} => {returnValue}");

                return returnValue;
            } catch (Exception exception) {
                Debug.WriteLine($"Error {functionCallAsString} : \n      Exception {exception.Message}\n{exception.StackTrace}");
            }
            return default(T);
        }


        [TestMethod]
        public void HandlersUnitTest() {
            var responseHandlers = new Dictionary<(string, HttpStatusCode), Func<RestResponse, dynamic?>> {
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

            var response = CallHandler("UnmatchRecords", HttpStatusCode.NoContent, responseHandlers);
            (response.Called as string).Should().Be("SuccessHandler");

            response = CallHandler(string.Empty, HttpStatusCode.NoContent, responseHandlers);
            (response.Called as string).Should().Be("SuccessDataHandler");

            response = CallHandler("Test", HttpStatusCode.OK, responseHandlers);
            (response.Called as string).Should().Be("SuccessDataHandler");

            response = CallHandler(string.Empty, HttpStatusCode.NotFound, responseHandlers);
            (response.Called as string).Should().Be("ErrorHandler");

        }

        private dynamic? CallHandler(string operation, HttpStatusCode statusCode, Dictionary<(string, HttpStatusCode), Func<RestResponse, dynamic?>> handlerDictionary) {
            var handler = handlerDictionary.FirstOrDefault(h => (h.Key.Item1 == operation || string.IsNullOrEmpty(h.Key.Item1)) && h.Key.Item2 == statusCode).Value;
            if (handler != null) 
                return handler(new RestResponse() { StatusCode = statusCode });
            return new { Called = "None" };
        }
        private dynamic? SuccessHandler(RestResponse response, string message) {
            Debug.WriteLine($"SuccessHandler called with '{message}'");
            return new { Called = "SuccessHandler" };
        }
        private dynamic? SuccessDataHandler(RestResponse response) {
            Debug.WriteLine($"SuccessDataHandler called");
            return new { Called = "SuccessDataHandler" };
        }
        private dynamic? ErrorHandler(RestResponse response, string message) {
            Debug.WriteLine($"ErrorHandler called with '{message}'");
            return new { Called = "ErrorHandler" };
        }
    }
}