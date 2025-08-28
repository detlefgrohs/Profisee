using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Common {
    public class RestfulMember {
        public dynamic Member { get; set; }
        public string Name {
            get { return (string)this.Get("Name"); }
            set { this.Set("Name", value); }
        }
        public string Code {
            get { return (string)this.Get("Code"); }
            set { this.Set("Code", value); }
        }
        public RestfulMember() {
            Member = new JObject();
        }
        public RestfulMember(dynamic member) {
            Member = member;
        }
        public RestfulMember(Dictionary<string, object> values) {
            Member = new JObject();
            foreach (var item in values)
                this.Set(item.Key, item.Value);
        }
        public T Get<T>(string name) {
            try {
                return (T)Convert.ChangeType(Get(name), typeof(T));
            } catch { }
            return default(T);
        }
        public object Get(string name) {
            foreach (var prop in Member.Children()) {
                if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase))
                    return prop.Value.Value; // Weird that we have to get the value of the value...
            }
            return null;
        }
        public void Set(string name, object value) {
            try {
                foreach (var prop in Member.Children()) {
                    if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase)) {
                        prop.Value = JToken.FromObject(value);
                        return;
                    }
                }
                if (value != null) // If we get here property was not in the member yet...
                    Member[name] = JToken.FromObject(value);
            } catch (Exception exception) {

            }
        }
    }
}
