import requests
from rich import print

BASE_SERVER_IP_ADDRESS = "http://127.0.0.1:8000"

def test_warning(text:str):
    print("[bold yellow][Warning!][/bold yellow]: " + text)

def test_alert(text:str):
    print("[bold red][Alert!][/bold red]: " + text)

def test_information(text:str):
    print("[bold][Information][/bold]: " + text)

def test_succeed(text:str):
    print("[bold green][Success!][/bold green]: " + text)


def default_path_test():
    response = None

    try:
        response = requests.get(BASE_SERVER_IP_ADDRESS)
    except requests.exceptions.ConnectionError:
        test_alert("Server is not responding, you may need to start it with \"fastapi dev\"")
        return
    
    responseDict = response.json()

    if responseDict["environment"] != "production" or responseDict["sourceURL"] != "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main" or responseDict["version"] == None:
        test_warning("Server didn't respond as expected in base path!")
        test_information("Response: \n" + str(responseDict))
    else:
        test_succeed("Default gateway responded correctly")


def feedback_test():
    TEST_FEEDBACK = "Hello, this is a feedback test"

    response = requests.post(BASE_SERVER_IP_ADDRESS + "/feedback",json={"feedback":TEST_FEEDBACK})

    if response.status_code != 204:
        test_alert("Feedback gateway unresponsive")
    else: 
        test_succeed("Feedback gateway responded correctly")


default_path_test()