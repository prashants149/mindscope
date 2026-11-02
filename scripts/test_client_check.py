from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "pong"}

client = TestClient(app)
response = client.get("/ping")
print("Response:", response.status_code, response.json())
