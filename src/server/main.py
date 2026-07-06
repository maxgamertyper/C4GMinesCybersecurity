from fastapi import FastAPI, status, Body
from fastapi.middleware.cors import CORSMiddleware
from server import utility, fileHandler, TestManager

app = FastAPI()
VERSION = "0.0.1"

# Allow the chrome extension/frontend to connect to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], # okay for development
    allow_credentials = True,
    allow_methods = ["GET","POST"],
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
def get_health():
    return {
        "status": "ok", 
        "timestamp": utility.get_time()
        }

#update this as we code tests, should be a string i.e "AI analysis"
@app.get("/tests")
def get_tests():
    return {
        "implementedTests": []
        }

# Temporary endpoint for frontend/backend testing. It receives email data from the Chrome extension and returns a placeholder
@app.post("/analyze", status_code=status.HTTP_200_OK)
def post_analyze(email: dict) :
    return {
        "score": 50,
        "threatLevel": "likely phishing",
        "reasons": ["This is a placeholder"],
        "passedTests": [],
        "failedTests": [
            {
                "testName": "placeholder_test",
                "testScore": 50,
                "testWeight": 1,
                "testPassed": False,
                "testDetails": "Placeholder"
            }
        ],
        "timestamp": utility.get_time(),
        "serverVersion": VERSION
    }

@app.post("/feedback", status_code=status.HTTP_200_OK)
def post_feedback(feedback:str = Body(embed=True)): # embeds the feedback field into the variable, could just use the payload as a dict if wanted
    print(feedback)
    fileHandler.write_feedback(feedback)
    return {
        "status": "received",
        "timestamp": utility.get_time()
        }


@app.post("/accuracy", status_code=status.HTTP_200_OK)
def post_accuracy(payload: dict):

    # store to database

    return {
        "timestamp": utility.get_time(),
        "status": "received"
        }