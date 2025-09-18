from datetime import datetime
from typing import Any
import json

from Profisee.Restful import API
from Profisee.Restful import GetOptions
from Profisee.Common import Common
# from Restful.Enums import ProcessActions, MatchingStatus, RequestOperation, WorkflowInstanceStatus


class Orchestration:
    def __init__(self, api: API):
        self.API = api

    def orchestrate(self, name: str):
        options = GetOptions()
        options.Filter = f"[Name] eq '{name}'"
        options.OrderBy = "[Step]"

        orchestration_steps = self.API.GetRecords("z_Orchestration", options)

        for step in orchestration_steps:
            process_type = Common.Get(step, "ProcessType", "")
            parameters_json = Common.Get(step, "Parameters", "{}")
            parameters = json.loads(parameters_json)

            self.run(process_type, parameters)




    def run(self, process_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        print(f"Running orchestration '{process_type}' with {parameters}...")




    def LogToProfisee(self, code: str, type: str, message: str) -> None:
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [{type}] : {code} {message}")
        response = self.API.MergeRecord("z_OrchestrationLog", {
            "Code": code,
            "Type": type,
            "Message": message})

print("Orchestration logging complete.")
if __name__ == "__main__":
    api = API("https://corpltr16.corp.profisee.com/profisee25r2", "0741a8cbebe54c2eae3d3b5cc4f49600", verify_ssl=False)
    print("Starting orchestration...")
    # run the orchestration
    orchestration = Orchestration(api)
    orchestration.orchestrate("Import")
