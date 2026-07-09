import os, sys, sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server.utility import DATABASE_FILE_PATH, VERSION
from server import utility, fileHandler




def table_exists(cursor, table_name: str):
    query = """
    SELECT EXISTS(
        SELECT 1 FROM sqlite_master 
        WHERE type='table' AND name=?
    );
    """
    cursor.execute(query, (table_name,))
    result = cursor.fetchone()
    
    return bool(result[0])

def table_analyzer(cursor, table_name):
    result = table_exists(cursor,table_name)
    if not result:
        utility.test_alert("Could not find table " + table_name, "Table: " + table_name)
    else:
        utility.test_succeed("Found table " + table_name, "Table: " + table_name)

def trigger_exists(cursor, trigger_name: str):
    query = """
    SELECT EXISTS(
        SELECT 1 FROM sqlite_master 
        WHERE type='trigger' AND name=?
    );
    """
    cursor.execute(query, (trigger_name,))
    result = cursor.fetchone()
    
    return bool(result[0])

def test_suspicious_actor():
    fileHandler.upload_suspicious_actor(conn,cursor,"testActor@testing.com","Email",20)

    cursor.execute(
    "SELECT * FROM suspicious_actors WHERE actorName = ? AND actorType = ?", 
    ("testActor@testing.com", "Email")
    )
    result = cursor.fetchone()

    thisID = cursor.lastrowid

    if not result:
        utility.test_alert("Could not find newly registered actor", "New Suspicious Actor")
    else:
        if result[0]==thisID and result[1]=="testActor@testing.com" and result[2]=="Email" and result[3]==20 and result[6]==1 and result[7]==0:
            utility.test_succeed("Recieved correct results for testActor@testing.com", "New Suspicious Actor")
        else:
            utility.test_alert("Recieved incorrect information for testActor@testing.com", "New Suspicious Actor")
            utility.test_information("Recieved: " + "\n".join(map(str,result)))
    
    #update test
    fileHandler.upload_suspicious_actor(conn,cursor,"testActor@testing.com","Email",40)

    cursor.execute(
    "SELECT * FROM suspicious_actors WHERE actorName = ? AND actorType = ?", 
    ("testActor@testing.com", "Email")
    )
    result = cursor.fetchone()

    if not result:
        utility.test_alert("Could not find previously registered actor", "Old Suspicious Actor")
    else:
        if result[0]==thisID and result[1]=="testActor@testing.com" and result[2]=="Email" and result[3]==30 and result[6]==2 and result[7]==0:
            utility.test_succeed("Recieved correct results for updated testActor@testing.com", "Old Suspicious Actor")
        else:
            utility.test_alert("Recieved incorrect information for testActor@testing.com", "Old Suspicious Actor")
            utility.test_information("Recieved: " + "\n".join(map(str,result)))


    #delete testing info
    delete_query = """
        DELETE FROM suspicious_actors
        WHERE actorName = ? AND actorType = ? 
    """
    delete_payload = (
        "testActor@testing.com", 
        "Email"
    )
    cursor.execute(delete_query,delete_payload)

    conn.commit()

def test_accuracy_return(conn,cursor):
    test_payload = {
        "body":"Hello, this is an accuracy placeholder body",
        "senderEmail": "testSender@testing.com",
        "senderName": "test Sender",
        "subject": "Testing Subject",
        "accuracy": True, # pressed yes on the extension
        "attachments": ["hi.exe","invoice.pdf"],
        "analysisReturn": {
            "score": 50,
            "threatLevel": "likely phishing",
            "reason": "This is a placeholder.",
            "passedTests": [
                {
                    "testName": "placeholder_test_passed",
                    "testScore": 100,
                    "testWeight": 50,
                    "testPassed": True,
                    "testDetails": "This is here to act as a success"
                }
            ],
            "failedTests": [
                {
                    "testName": "placeholder_test_failed",
                    "testScore": 0,
                    "testWeight": 50,
                    "testPassed": False,
                    "testDetails": "This is here to act as a failure"
                }
                ],
            }
        }
    fileHandler.process_accuracy(conn,cursor,test_payload)

    #email test
    emailID = _test_email(test_payload,cursor)
    
    #test attachments
    _test_attachments(emailID,cursor)

    #test analysis_feedback
    submissionID = _test_feedback(emailID,cursor)

    #tests test
    _test_tests(submissionID,cursor)

    cursor.execute("""
        DELETE FROM emails_table
        WHERE emailID = ?
    """,(emailID,))

    conn.commit()

def _test_email(test_payload: dict, cursor):
    cursor.execute("""
        SELECT * FROM emails_table
        WHERE body = ?
    """, (test_payload["body"],))
    response = cursor.fetchone()

    email_id = response[0]

    if not response:
        utility.test_alert("Couldn't find email from test_payload")
        return 0

    if response[1]==test_payload["senderName"] and response[2]==test_payload["senderEmail"] and response[3]==test_payload["subject"] and response[4]==test_payload["body"]:
        utility.test_succeed("Found email from test_payload","Accuracy Test")
    else:
        utility.test_alert("Incorrect information from email in test_payload", "Accuracy Test")
        return email_id
    
    return email_id

def _test_attachments(emailID, cursor):
    cursor.execute("""
        SELECT * FROM attachments_table
        WHERE emailID = ?
    """, (emailID,))
    attachments = cursor.fetchall()

    if len(attachments)!=2:
        utility.test_alert("Could not find all attachments with test_payload","Accuracy Test")
    
    if len(attachments)==0:
        utility.test_alert("Could not find any attachments for test_payload","Accuracy Test")
    
    names = ["hi","invoice"]
    extensions = [".exe",".pdf"]

    for item in attachments:
        if item[1]==emailID and item[2] in names and item[3] in extensions:
            utility.test_succeed("Correct information for Attachment: " + item[2] + item[3], "Accuracy Test")
        else:
            utility.test_alert("Incorrect information for Attachment: "+ item[2] + item[3], "Accuracy Test")
            utility.test_information("Recieved: "+"\n".join(map(str,item)))
    
def _test_feedback(emailID, cursor):
    cursor.execute("""
        SELECT * FROM analysis_feedback
        WHERE emailID = ?
    """, (emailID,))
    feedback = cursor.fetchone()

    if not feedback:
        utility.test_alert("Could not find any feedback for test_payload", "Accuracy Test")
        return 0
    
    if feedback[1]==emailID and feedback[3]==1 and feedback[4]==VERSION and feedback[5]==50 and feedback[6]=="likely phishing" and feedback[7]=="This is a placeholder.":
        utility.test_succeed("Correct feedback Information for test_payload", "Accuracy Test")
    else:
        utility.test_alert("Invalid results from feedback", "Accuracy Test")
        utility.test_information("Recieved: "+"\n".join(map(str,feedback)))
    
    return feedback[0]

def _test_tests(submissionID, cursor):
    cursor.execute("""
        SELECT * FROM tests_table
        WHERE submissionID = ?
    """, (submissionID,))
    tests = cursor.fetchall()

    if len(tests)!=2:
        utility.test_alert("Could not find all tests with test_payload","Accuracy Test")
    
    if len(tests)==0:
        utility.test_alert("Could not find any tests for test_payload","Accuracy Test")

    for test in tests:
        if test[5]==0 and test[4]=="placeholder_test_failed" and test[3]==50 and test[2]==0 and test[1]==submissionID:
            utility.test_succeed("Found Failed test in test_payload", "Accuracy Test")
        elif test[5]==1 and test[4]=="placeholder_test_passed" and test[3]==50 and test[2]==100 and test[1]==submissionID:
            utility.test_succeed("Found Passed test in test_payload", "Accuracy Test")
        else:
            utility.test_alert("Incorrect information for Test: "+ test[4], "Accuracy Test")
            utility.test_information("Recieved: "+"\n".join(map(str,test)))

if __name__ == "__main__":
    conn = sqlite3.connect(DATABASE_FILE_PATH, check_same_thread=False)
    cursor = conn.cursor()

    #Check for existence
    fileHandler.create_if_nonesxistent(conn,cursor)

    table_analyzer(cursor,"suspicious_actors")
    table_analyzer(cursor,"emails_table")
    table_analyzer(cursor,"attachments_table")
    table_analyzer(cursor,"analysis_feedback")
    table_analyzer(cursor,"tests_table")

    if not trigger_exists(cursor, "update_actor_last_seen"):
        utility.test_alert("Could not find trigger update_actor_last_seen", "Trigger: update_actor_last_seen")
    else:
        utility.test_succeed("Found trigger update_actor_last_seen", "Trigger: update_actor_last_seen")


    #actor test
    test_suspicious_actor()

    #accuracy endpoint
    test_accuracy_return(conn, cursor)