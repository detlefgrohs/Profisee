using Common;
using System.Diagnostics;

namespace UnitTests
{
    [TestClass]
    public sealed class UnitTests
    {
        [TestMethod]
        public void TestMethod1()
        {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";

            var restfulAPI = new RestfulAPI(profiseeUri, clientId, LoggerAction);

            var members = restfulAPI.GetMembers("Test", new RestfulAPI.GetOptions());
        }
        public void LoggerAction(LogLevel level, string message)
        {
            Debug.WriteLine($"{level}: {message}");
        }
    }
}
