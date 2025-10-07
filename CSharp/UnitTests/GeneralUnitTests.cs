using Profisee.MDM;
using System.Diagnostics;

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
    }
}
