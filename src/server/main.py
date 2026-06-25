from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

# To start the server run "fastapi dev ./src/server/main.py"


@app.get("/health")
def read_root():
    return {
        "status": "ok", 
        "timestamp": datetime.now(timezone.utc).isoformat()
        }