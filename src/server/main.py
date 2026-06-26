from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()
VERISON = "0.0.1"

# To start the server run "fastapi dev ./src/server/main.py"
@app.get("/")
def read_root():
    return {
        "sourceURL": "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main",
        "version": VERISON,
        "environment": "production"
        }

@app.get("/health")
def read_root():
    return {
        "status": "ok", 
        "timestamp": datetime.now(timezone.utc).isoformat()
        }

#update this as we code tests, should be a string i.e "AI analysis"
@app.get("/tests")
def read_root():
    return {
        "implementedTests": []
        }