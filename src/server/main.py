from fastapi import FastAPI, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from server import utility, fileHandler
from contextlib import asynccontextmanager
import os
import sqlite3


VERSION = "0.0.1"

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE_PATH = os.path.join(CURRENT_DIR, "sushiSQL.db")

@asynccontextmanager
async def server_wrapper(app: FastAPI):
    #run before the server starts accepting requests
    conn = sqlite3.connect(DATABASE_FILE_PATH, check_same_thread=False)
    cursor = conn.cursor()

    fileHandler.create_if_nonexistent(conn, cursor)

    #store them in fastAPI
    app.state.db_conn = conn
    app.state.db_cursor = cursor

    yield # let the server do stuff

    conn.close() # close after the server shuts off

app = FastAPI(lifespan=server_wrapper)

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
        "reason": "This is a placeholder.",
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
        "receivedEmail": email,
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
def post_accuracy(payload: dict, request: Request):

    {
        "body":"Hello, this is an accuracy placeholder body",
        "sender": "sender@placeholder.com",
        "subject": "Placeholder Subject",
        "accuracy": True, # pressed yes on the extension
        "attachments": ["hi.exe","suspicious.xlsx"],
        "analysisReturn": {
            "score": 50,
            "threatLevel": "likely phishing",
            "reason": "This is a placeholder.",
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
            }
        }
    # store to database

    return {
        "timestamp": utility.get_time(),
        "status": "received"
        }