using FluentAssertions;
using Newtonsoft.Json.Linq;
using Profisee.MDM;
using System.Diagnostics;
using static System.Net.Mime.MediaTypeNames;

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
            //var response = restfulAPI.RunConnectBatch("SQL Server [DQParent] Export [dbo].[tbl_DQParent]");

            var response = restfulAPI.RunConnectBatch("SQL Server [dbo].[tbl_Test] Import [Test]");

            if (restfulAPI.StatusCode == System.Net.HttpStatusCode.BadRequest) {
                // Check for empty Strategy Error
                var errors = restfulAPI.Errors;

                if (errors is JArray) {
                    errors = errors[0];
                }


                foreach (var error in errors) {
                    var innerError = error;
                }
            }
        }

        [TestMethod]
        public void ProcessMatchingActionsTest() { 
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);
            var response = restfulAPI.ProcessMatchingActions("MatchingTest");

            //response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.SurvivorshipOnly);

            response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.MatchingAndSurvivorship);

            //response = restfulAPI.ProcessMatchingActions("MatchingTest", ProcessAction.ClearPriorResults);
        }


        [TestMethod]
        public void GetAttributesTest() {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var allAttributes = restfulAPI.GetAttributes();
            int allAttributesCount = allAttributes.Count;

            allAttributesCount.Should().BeGreaterThan(0);

            var attributesForEntity = restfulAPI.GetAttributes("Test");
            int attributesForEntityCount = attributesForEntity.Count;

            attributesForEntityCount.Should().BeLessThan(allAttributesCount);
        }

        [TestMethod]
        public void GetRecordTest() {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var record = restfulAPI.GetRecord("Orchestration", "z_SETTINGS");
            ((object)record).Should().NotBeNull();
            var name = RestfulAPI.GetPropertyValue(record, "Name", "") as string;
            name.Should().Be("z_Settings");
        }

        [TestMethod]
        public void MergeRecordTest() {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var response = restfulAPI.MergeRecord("Orchestration", new {
                Name = "z_SETTINGS2",
                Code = "z_SETTINGS2",
                Parameters = "{\"Setting1\":\"Value1\",\"Setting2\":\"Value2\"}"
            });
        }

        [TestMethod]
        public void GeneralTest() {
            var profiseeUri = @"https://corpltr16.corp.profisee.com/Profisee25r2";
            var clientId = @"0741a8cbebe54c2eae3d3b5cc4f49600";
            var restfulAPI = new Profisee.MDM.RestfulAPI(profiseeUri, clientId, LoggerAction);

            var memberFromGetMember = restfulAPI.GetMember("Orchestration", "z_SETTINGS");

            var parametersFromMember = RestfulAPI.GetPropertyValue(memberFromGetMember, "Parameters", "{}") as string;

            var memberFromGetRecord = restfulAPI.GetRecord("Orchestration", "z_SETTINGS");

            var parametersFromRecord = RestfulAPI.GetPropertyValue(memberFromGetRecord, "Parameters", "{}") as string;

            parametersFromMember.Should().NotBe("{}");
            parametersFromRecord.Should().NotBe("{}");

            parametersFromMember.Should().Be(parametersFromRecord);



        }


        public void LoggerAction(LogLevel level, string message)
        {
            Debug.WriteLine($"{level}: {message}");
        }
    }
}
