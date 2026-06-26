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
    
    if response.status_code != 200:
        test_alert("Default gateway responded incorrectly")
        return

    responseDict = response.json()

    try:
        if responseDict["environment"] != "production" or responseDict["sourceURL"] != "https://github.com/maxgamertyper/C4GMinesCybersecurity/tree/main" or responseDict["version"] == None:
            test_warning("Server didn't respond as expected in base path!")
            test_information("Response: \n" + str(responseDict))
        else:
            test_succeed("Default gateway responded correctly")
    except KeyError:
        test_alert("Missing informaiton detected in default gateway!")
        test_information("Response: \n" + str(responseDict))


def health_test():
    response = None

    try:
        response = requests.get(BASE_SERVER_IP_ADDRESS + "/health")
    except requests.exceptions.ConnectionError:
        test_alert("Server is not responding, you may need to start it with \"fastapi dev\"")
        return

    if response.status_code != 200:
        test_alert("Health gateway responded incorrectly")
        return
    
    responseDict = response.json()

    try:
        if responseDict["status"] != "ok" or responseDict["timestamp"] == None:
            test_warning("Server didn't respond as expected in \"/health\" path!")
            test_information("Response: \n" + str(responseDict))
        else:
            test_succeed("Health gateway responded correctly")
    except KeyError:
        test_alert("Missing informaiton detected in \"/health\" path!!")
        test_information("Response: \n" + str(responseDict))



def feedback_test():
    TEST_FEEDBACK = "Hello, this is a feedback test"

    response = None

    try:
        response = requests.post(BASE_SERVER_IP_ADDRESS + "/feedback",json={"feedback":TEST_FEEDBACK})
    except requests.exceptions.ConnectionError:
        test_alert("Server is not responding, you may need to start it with \"fastapi dev\"")
        return

    if response.status_code != 204:
        test_alert("Feedback gateway responded incorrectly in \"/feedback\" path!")
    else: 
        test_succeed("Feedback gateway responded correctly")



default_path_test()
health_test()
feedback_test()