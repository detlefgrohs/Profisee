from typing import Any, Dict
import uvicorn
from fastapi import FastAPI, Request, Body

app = FastAPI()

@app.get("/status")
async def status():    
    print("Status page called")
    return {"message": "Status called successfully!"}

@app.post("/webhook")
async def webhook(request: Request = None):
    body = await request.body()
    if len(body) != 0 :
        data = await request.json()
        print("Received webhook data:", data)
    else:
        print("Received no webhook data.")
    return {"message": "Webhook received successfully!"}

@app.post("/webhook_request")
async def webhook(request: Dict[str, Any] = None):
    data = request
    print("Received webhook data:", data)
    return {"message": "Webhook received successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
