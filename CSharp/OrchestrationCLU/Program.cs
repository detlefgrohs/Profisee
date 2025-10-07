using CommandLineParser.Arguments;
using Profisee.MDM;
using Newtonsoft.Json;
using System.ComponentModel;

namespace Profisee.MDM.OrchestrationCLU
{
    class CommandLineOptions
    {
        [SwitchArgument('h', "help", false, Description = "")]
        public bool ShowHelp { get; set; }

        [SwitchArgument('t', "test", false, Description = "")]
        public bool Test { get; set; }

        [SwitchArgument('w', "whatif", false, Description = "")]
        public bool WhatIf { get; set; }

        [ValueArgument(typeof(string), 'n', "name", Description = "")]
        public string? Name { get; set; }

        [ValueArgument(typeof(string), 'p', "profiseeurl", Description = "")]
        public string? ProfiseeUrl { get; set; }

        [ValueArgument(typeof(string), 'c', "clientid", Description = "")]
        public string? ClientId { get; set; }

        [ValueArgument(typeof(string), 'o', "orchestrationprocesstype", Description = "")]
        public string? ProcessType { get; set; }

        [ValueArgument(typeof(string), 's', "settings", Description = "")]
        public string? Settings { get; set; }
    }


    internal class Program
    {
        static int Main(string[] args)
        {
            var commandLineOptions = new CommandLineOptions();
            CommandLineParser.CommandLineParser parser = new CommandLineParser.CommandLineParser();
            parser.ExtractArgumentAttributes(commandLineOptions);
            parser.ParseCommandLine(args);

            if (commandLineOptions.ShowHelp)
            {
                parser.ShowUsage();
                return 0;
            }

            // Load settings.json
            dynamic settings = LoadSettings();

            var profiseeUrl = Orchestration.GetPropertyValue(settings, "ProfiseeUrl", "") as string;
            if (!string.IsNullOrEmpty(commandLineOptions.ProfiseeUrl))
                profiseeUrl = commandLineOptions.ProfiseeUrl;

            var clientId = Orchestration.GetPropertyValue(settings, "ClientId", "") as string;
            if (!string.IsNullOrEmpty(commandLineOptions.ClientId))
                clientId = commandLineOptions.ClientId;

            if (string.IsNullOrEmpty(profiseeUrl) || string.IsNullOrEmpty(clientId))
            {
                Console.WriteLine("ProfiseeUrl and ClientId are required.");
                Console.WriteLine();
                parser.ShowUsage();
                return 1;   
            }


            Console.WriteLine("Profisee.MDM.Orchestration:");
            Console.WriteLine($"ProfiseeUrl: {profiseeUrl}");
            Console.WriteLine($"ClientId: {clientId}");
            
            var api = new RestfulAPI(profiseeUrl, clientId, LoggerAction);

            if (commandLineOptions.Test)
            {
                var entities = api.GetEntities();

                if (api.StatusCode != System.Net.HttpStatusCode.OK)
                {
                    Console.WriteLine($"Failed to connect to Profisee. Error: {api.StatusCode}");
                    return 1;
                }

                var entity_count = Orchestration.GetPropertyValue(entities, "TotalRecords", 0);
                Console.WriteLine($"Connected to Profisee. Found {entity_count} entities.");
                return 0;
            }


            if (string.IsNullOrEmpty(commandLineOptions.Name))
            {
                Console.WriteLine("Name is required.");
                Console.WriteLine();
                parser.ShowUsage();
                return 1;
            }


            if (string.IsNullOrEmpty(commandLineOptions.ProcessType))
            {
                Console.WriteLine($"Running Orchestration '{commandLineOptions.Name}' from Instance");
                var orchestration = new Orchestration(api, LoggerAction);
                orchestration.WhatIf = commandLineOptions.WhatIf;
                var (returnCode, message) = orchestration.Orchestrate(commandLineOptions.Name);
                Console.WriteLine(message);
                return returnCode;
            } else
            {
                Console.WriteLine($"Running Process '{commandLineOptions.Name}' {commandLineOptions.ProcessType} with '{commandLineOptions.Settings}'");

            }

            return 0;
        }
        public static void LoggerAction(LogLevel logLevel, string message)
        {
            Console.WriteLine($"[{logLevel}] {message}");
        }
        public static dynamic LoadSettings()
        {
            try
            {
                using StreamReader r = new StreamReader("settings.json");
                    return Orchestration.ParseJson(r.ReadToEnd(), "{}");
            }
            catch (Exception)
            {
                Console.WriteLine("No settings.json file found, using defaults.");
            }
            return Orchestration.ParseJson("{}", string.Empty);
        }

        //public static object GetPropertyValue(dynamic obj, string name, object defaultValue)
        //{
        //    foreach (var prop in obj.Children())
        //    {
        //        if (((string)prop.Name).Equals(name, StringComparison.InvariantCultureIgnoreCase))
        //            return prop.Value.Value; // Weird that we have to get the value of the value...
        //    }
        //    return defaultValue;
        //}
    }
}
