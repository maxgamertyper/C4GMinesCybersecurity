from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

# To start the server run "fastapi dev ./src/server/main.py"
@app.get("/")
def read_root():
    return {
        "sourceURL": "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main",
        "version": "1.0.0",
        "environment": "production"
        }

@app.get("/health")
def read_root():
    return {
        "status": "ok", 
        "timestamp": datetime.now(timezone.utc).isoformat()
        }