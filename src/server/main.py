from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from datetime import datetime, timezone

app = FastAPI()
VERSION = "0.0.1"

# Allows the chrome extension/frontend to communicate w/ the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


# To start the server run "fastapi dev ./src/server/main.py"
@app.get("/")
def read_root():
    return {
        "sourceURL": "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main",
        "version": VERSION,
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

# TEMPORARY analyze endpoint. this will call the actual phishing tests and scoring system later
@app.post("/analyze")
def analyze_email(email: dict) :
    return {
        "score": 50,
        "threatLevel": "Likely phishing",
        "reason": "It looks suspicious.",
        "passedTests": [],
        "failedTests": [
            {
                "testName": "placeholder_test",
                "details": "Backend received the email data successfully."
            }
        ],
        "receivedEmail": email

    }

# TEMPORARY feedback endpoint. This will store user feedback in the database later
@app.post("/feedback")
def submit_feedback(feedback: dict) :
    return{
        "status": "recieved",
        "feedback": feedback
    }