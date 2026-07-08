from fastapi import FastAPI, status, Body
from fastapi.middleware.cors import CORSMiddleware
from server import utility
from server import fileHandler

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

# sample attachments phishing test
RISKY_ATTACHMENTS = [".exe", ".iso", ".scr", ".bat", ".cmd", ".js", ".vbs", ".zip"]

# checks filenames
def check_attachments(attachments: list):
    failed_tests = []

    for attachment in attachments :
        lower_attachment = attachment.lower()

        # checking the ending of the attachments for risky extensions
        for extension in RISKY_ATTACHMENTS :
            if lower_attachment.endswith(extension) :
                failed_tests.append({
                    "testName": "attachment_check",
                    "testScore": 20,
                    "testWeight": 1,
                    "testPassed": False,
                    "testDetails": f"Suspicious attachment detected: {attachment}"
                })
    
    # return all the failed attachment tests
    return failed_tests

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
        "implementedTests": [
            "attachment_check"
        ]
        }

# Temporary endpoint for frontend/backend testing
# It receives email data from the Chrome extension and returns a basic phishing anaylsis for attachments
@app.post("/analyze", status_code=status.HTTP_200_OK)
def post_analyze(email: dict) :

        """
        Expected input example:
        {
            "body": "Email body text",
            "sender": "sender@example.com",
            "subject": "Email subject",
            "attachments": ["invoice.exe", "notes.pdf"]
        }

        Current behaviour:
        - extracts attachments from request body
        - runs attachment_check
        - calculates a simple score (?)
        - returns score, threat level, reason, passed tests, and failed tests
        """
        # Get attachments from email payload. If no attachments exist, it will use an empty list
        attachments = email.get("attachments", [])

        # run attachment checker. Risky attachments are returned as failed tests
        failed_tests = check_attachments(attachments)
        
        # store passed tests
        passed_tests = []

        # if no risky attachments found, mark attachment_check as passed
        if len(failed_tests) == 0 :
            passed_tests.append({
                "testName": "attachment_check",
                "testScore": 0,
                "testWeight": 1,
                "testPassed": True,
                "testDetails": "No risky attachment extensions detected."
            })
        
        # calculate total phishing score by adding failed test scores
        score = sum(test["testScore"] for test in failed_tests)

        # convert numeric score into a user-readable threat level
        if score >= 40 :
            threat_level = "likely phishing"
        elif score >= 20 :
            threat_level = "suspicious"
        else :
            threat_level = "safe"

        # create a short explanantion for frontend display
        if failed_tests :
            reason = "This email contains one or more risky attachment types."
        else :
            reason = "No risky attachment types were detected."

        # return the analysis result
        return {
            "score": score,
            "threatLevel": threat_level,
            "reason": reason,
            "passedTests": passed_tests,
            "failedTests": failed_tests,
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
def post_accuracy(payload: dict):

    # store to database

    return {
        "timestamp": utility.get_time(),
        "status": "received"
        }