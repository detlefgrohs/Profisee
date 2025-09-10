from typing import Any, Dict
import uvicorn
import pyodbc
from fastapi import FastAPI, Request, Body
from Profisee.Restful import API
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


api = API("https://corpltr16.corp.profisee.com/profisee25r2", "0741a8cbebe54c2eae3d3b5cc4f49600", verify=False)
app = FastAPI(openapi_url="/Python/openapi.json")
app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["*"], # Adjust as necessary
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
                )

class WorkflowRequest(BaseModel):
    pass

@app.post("/TestWorkflowActivity")
async def TestWorkflowActivity(request: Dict[str, Any]):
    # data = await request.json()
    data = request

    entityName = data["MemberDataContext"]["EntityId"]["Name"]
    memberCode = data["MemberDataContext"]["Code"]
        
    isTestEntity = True if entityName == "Z_WorkflowTest" else False
    testFlowMessage = ""
    
    if isTestEntity :
        connectionStringMember = api.GetRecord("Z_Settings", "SQLCONNECTIONSTRING")
        
        if connectionStringMember != None :
            member = api.GetRecord(entityName, memberCode)
            input = member["name"] if member != None else "not found"
            
            connection = pyodbc.connect(connectionStringMember["value"])
            cursor = connection.cursor()
            cursor.execute("SELECT [dbo].[TestWorkflow] (?)", input)
            result = cursor.fetchval() == input
            
            testFlowMessage = "Test logic executed. Your input: " + input + ". Are other connections and data valid: " + str(result)
                                            
            print(testFlowMessage)
                                            
    returnValue = { "ProcessingStatus" : 0,
                    "ResponsePayload" :
                        { 
                            "IsTest" : isTestEntity,
                            "TestFlowMessage" : testFlowMessage
                        }
                    }
    return returnValue



@app.get("/openapi.json")
async def openapi():    
    print("openapi page called")
    return app.openapi()

@app.get("/status")
async def status():    
    print("Status page called")
    return {"message": "Status called successfully!"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("Received webhook data:", data)
    return {"message": "Webhook received successfully!"}

@app.post("/workflowwebhook")
async def workflowwebhook(request: Dict[str, Any]):
    # data = await request.json()
    print("Received workflowwebhook data:", request)
    returnValue = { "ProcessingStatus" : 1234,
             "ResponsePayload" :
                { "message": "workflowwebhook received successfully!",
                  "returndata" : str(request),
                  "IsTestWorkflow" : True
                }
            }
    print(returnValue)
    return returnValue




# OUTPUT_FILE = # Path(__file__).parent / 'openapi.json'
# OUTPUT_FILE.write_text(json.dumps(app.openapi(), indent=2))

# with open(r"C:\inetpub\wwwroot\Python\openapi.json", "w") as file :
#     file.write(json.dumps(app.openapi(), indent=2))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
