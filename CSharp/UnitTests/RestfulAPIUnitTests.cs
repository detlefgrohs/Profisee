using Profisee.MDM;
using System.Diagnostics;

namespace Profisee.MDM.UnitTests
{
    [TestClass]
    public sealed class RestfulAPIUnitTests
    {
        [TestMethod]
        public void GetMembersTest()
        {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";

            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var members = restfulAPI.GetMembers("Test", new Profisee.MDM.RestfulAPI.GetOptions());
        }
        [TestMethod]
        public void MergeMemberTest() {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var response = restfulAPI.MergeMember("Test", new RestfulMember(new Dictionary<string, object> {
                { "Name", Guid.NewGuid().ToString() },
                { "Test2", 123 }
            }).Member);

            response = restfulAPI.MergeMember("Test", new { Name = "Test2", Test2 = 123 });

            response = restfulAPI.MergeMembers("Test", new List<dynamic> {
                new { Name = "Test3", Test2 = 456 },
                new { Name = "Test4", Test2 = 789 }
            });
        }
        [TestMethod]
        public void GetMonitorActivitiesTest()
        {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);
            var activities = restfulAPI.GetMonitorActivities();
        }

        [TestMethod]
        public void RunConnectBatchTest()
        {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);
            var response = restfulAPI.RunConnectBatch("SQL Server [DQParent] Export [dbo].[tbl_DQParent]");
        }

        [TestMethod]
        public void ProcessMatchingActionsTest() { 
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);
            var response = restfulAPI.ProcessMatchingActions("MatchingTest");

            response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.SurvivorshipOnly);

            response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.MatchingAndSurvivorship);

            response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.ClearPriorResults);
        }




        public void LoggerAction(LogLevel level, string message)
        {
            Debug.WriteLine($"{level}: {message}");
        }
    }
}
