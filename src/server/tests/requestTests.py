import requests
from rich import print
from dataclasses import dataclass

BASE_SERVER_IP_ADDRESS = "http://127.0.0.1:8000"


@dataclass
class RouteTestRecord:
    routeAddress: str # the address of the endpoint i.e "/" or "/health"
    responsePayload: dict # how the json response should look {"key": "value"} for a specific response {"key": None} for a generic response that just includes the key
    statusCode: int # the wanted return status code, 200 is mainly for gets
    routeName: str # the name i.e "Root", "Tests", "Health"
    isGET: bool # whether its a get or post request, feedback is a POST, health and tests are GET
    postPayload: dict = None # if isGET is false, this will send a post request with this payload instead of a get



#once all tests are made, append them to master test list
MASTER_ROUTE_TEST = []

# the expected response for root aka "/"
expectedRootPayload = {
    "sourceURL": "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main",
    "version": None, # means that it can reply with anything, just checking if the key is present
    "environment": "production"
    }
rootEndpoint = RouteTestRecord(
    routeAddress = "/",
    responsePayload = expectedRootPayload,
    statusCode = 200,
    routeName = "Root",
    isGET = True
    )
MASTER_ROUTE_TEST.append(rootEndpoint)

# /tests endpoint
expectedTestsPayload = {
    "implementedTests": None # check if key is present
    }
testsEndpoint = RouteTestRecord(
    routeAddress = "/tests",
    responsePayload = expectedTestsPayload,
    statusCode = 200,
    routeName = "Tests",
    isGET = True
    )
MASTER_ROUTE_TEST.append(testsEndpoint)

# /health endpoint
expectedHealthPayload = {
    "status": "ok", 
    "timestamp": None # check if present
    }
healthEndpoint = RouteTestRecord(
    routeAddress = "/health",
    responsePayload = expectedHealthPayload,
    statusCode = 200,
    routeName = "Health",
    isGET = True
    )
MASTER_ROUTE_TEST.append(healthEndpoint)

# /feedback endpoint
expectedFeedbackPayload = {
    "timestamp": None,
    "status": "received"
}
feedbackEndpoint = RouteTestRecord(
    routeAddress = "/feedback",
    responsePayload = expectedFeedbackPayload,
    statusCode = 200,
    routeName = "Feedback",
    isGET = False,
    postPayload = {"feedback":"Hello, this is a feedback test"}
    )
MASTER_ROUTE_TEST.append(feedbackEndpoint)

# /analyze endpoint
expectedanalyzePayload = {
    "score": None,
    "threatLevel": None,
    "reason": None,
    "passedTests": None,
    "failedTests": None,
    "receivedEmail": None,
    "timestamp": None,
    "serverVersion": None
}
analyzeEndpoint = RouteTestRecord(
    routeAddress = "/analyze",
    responsePayload = expectedanalyzePayload,
    statusCode = 200,
    routeName = "Analyze",
    isGET = False,
    postPayload = {
        "body":"Hello, this is an accuracy placeholder body",
        "sender": "sender@placeholder.com",
        "subject": "Placeholder Subject",
        "accuracy": True,
        "attachments": ["hi.exe","suspicious.xlsx"]
        }
    )
MASTER_ROUTE_TEST.append(analyzeEndpoint)

# /accuracy
expectedAccuracyPayload = {
    "timestamp": None,
    "status": "received"
}
accuracyEndpoint = RouteTestRecord(
    routeAddress = "/accuracy",
    responsePayload = expectedAccuracyPayload,
    statusCode = 200,
    routeName = "Accuracy",
    isGET = False,
    postPayload = {
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
    )
MASTER_ROUTE_TEST.append(accuracyEndpoint)


# the differnt print statements for tests
# the \\ is an escape sequence so the Rich library doesn't treat it as mark up and instead just a normal string
def test_warning(text:str, routeName: str):
    print("[bold yellow]\\[Warning from " + routeName + "!][/bold yellow]: " + text)

def test_alert(text:str, routeName: str):
    print("[bold red]\\[Alert from " + routeName + "!][/bold red]: " + text)

def test_information(text:str):
    print("[bold]\\[Information][/bold]: " + text)

def test_succeed(text:str, routeName: str):
    print("[bold green]\\[" + routeName + " Succeeded!][/bold green]: " + text)


# the actual test module
def route_test(routeTestInformation: RouteTestRecord):
    # generic response object
    response = None

    #cleaning up the variables in the record holder
    routeAddress = routeTestInformation.routeAddress
    cleanName = "\""+routeTestInformation.routeName+"\""
    expectedStatusCode = routeTestInformation.statusCode
    isGETRequest = routeTestInformation.isGET
    postPayload = routeTestInformation.postPayload

    #testing malformed
    if isGETRequest==False and postPayload==None:
        test_alert("Malformed test body, set as post request with no post body", cleanName)
        return
    elif isGETRequest==True and postPayload!=None:
        test_alert("Malformed test body, set as get request with a set post body", cleanName)
        return

    #default connection test
    try:
        if isGETRequest:
            response = requests.get(BASE_SERVER_IP_ADDRESS + routeAddress)
        else:
            response = requests.post(BASE_SERVER_IP_ADDRESS + routeAddress, json=postPayload)
        
    except requests.exceptions.ConnectionError:
        test_alert("Server is not responding, you may need to start it with \"fastapi dev\"", cleanName)
        return
    
    recievedStatusCode = response.status_code

    #staus code check
    if recievedStatusCode != expectedStatusCode:
        test_alert("Responded incorrectly", cleanName)
        test_information("Recieved status code: " + str(recievedStatusCode) + "\nExpected: " + str(expectedStatusCode))
        return

    # payload check
    responseDict = response.json()
    expectedPayload = routeTestInformation.responsePayload

    #if the response has more keys, it has another body answer
    if len(responseDict.keys()) > len(expectedPayload.keys()):
        test_warning("Responded with extra information", cleanName)

    # check for key matches in the response and record
    for key in expectedPayload.keys():
        try:
            expectedValue = expectedPayload[key]
            valueExists = expectedValue!=None

            #if the expected value is set and it doesnt equal it
            if valueExists and responseDict[key]!=expectedValue:
                test_warning("Unexpected key value", cleanName)
                test_information("Expected: {" + key + ": " + expectedValue + "}\nGot: {" + key + ": " + responseDict[key] + "}")
            #if the value should exist and the key is there but has no value
            if not valueExists and responseDict[key]==None:
                test_alert("Expected " + key + " to have a value, recieved None", cleanName)
                return
            
        except KeyError: # if the key isnt in the response
            test_alert("Missing informaiton detected (key: " + key + ")", cleanName)
            test_information("Response: \n" + str(responseDict))
            return
    
    
    test_succeed("responded correctly", routeTestInformation.routeName) # not clean name as it looks weird with quotes


# the master loop that checks every test and actually tests it
def test_endpoints(MASTER_ROUTE_TEST: list):
    for routeTestRecord in MASTER_ROUTE_TEST:
        cleanName = "\""+routeTestRecord.routeName+"\""
        cleanAddress = "\""+routeTestRecord.routeAddress+"\""

        print("[bold blue]Testing Route: " + cleanName + " at "+ cleanAddress + "[/bold blue]")

        route_test(routeTestRecord)

test_endpoints(MASTER_ROUTE_TEST)