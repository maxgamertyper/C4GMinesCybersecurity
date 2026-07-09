from server import utility
from server.main import VERSION
import os

# change directory to the same as the file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE_PATH = os.path.join(CURRENT_DIR, "feedback.txt")





#silly text writing
def write_feedback(feedback:str):

    with open(FEEDBACK_FILE_PATH,"a+") as feedbackFile:
        feedbackFile.write(utility.get_time() + "\n" + feedback + "\n\n")

        feedbackFile.close()
    
    return


#sql
def create_if_nonesxistent(conn, cursor):
    cursor.execute("PRAGMA foreign_keys = ON;") # enforce foreign key rules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suspicious_actors (
        actorID INTEGER PRIMARY KEY AUTOINCREMENT,
        actorName TEXT UNIQUE,
        actorTYPE TEXT,
        suspicionLevel INTEGER,
        firstSeen DATETIME DEFAULT CURRENT_TIMESTAMP,
        lastSeen DATETIME DEFAULT CURRENT_TIMESTAMP,
        occurrences INTEGER,
        manualConfirmation BOOLEAN
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails_table (
        emailID INTEGER PRIMARY KEY AUTOINCREMENT,
        senderName TEXT,
        senderEmail TEXT,
        subject TEXT,
        body TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attachments_table (
        attachmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        emailID INTEGER,
        attachmentName TEXT,
        attachmentExtension TEXT,
        
        FOREIGN KEY (emailID) REFERENCES emails_table(emailID)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_feedback (
        submissionID INTEGER PRIMARY KEY AUTOINCREMENT,
        emailID INTEGER,
        submissionTime DATETIME DEFAULT CURRENT_TIMESTAMP,
        userAccuracyResponse BOOLEAN,
        serverVersion TEXT,
        phishingScore INTEGER,
        phishingType TEXT,
        reason TEXT,
        
        FOREIGN KEY (emailID) REFERENCES emails_table(emailID)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tests_table (
        testID INTEGER PRIMARY KEY AUTOINCREMENT,
        submissionID INTEGER,
        testScore INTEGER,
        testWeight INTEGER,
        testName TEXT,
        testPassed BOOLEAN,
        
        FOREIGN KEY (submissionID) REFERENCES analysis_feedback(submissionID)
    )
    """)


    # Trigger is used to autmatically update the lastSeen value when the item is updated
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS update_actor_last_seen
    AFTER UPDATE ON suspicious_actors
    BEGIN
        UPDATE suspicious_actors 
        SET lastSeen = CURRENT_TIMESTAMP 
        WHERE actorID = NEW.actorID;
    END;
    """)
    conn.commit()

def process_accuracy(conn, cursor, payload: dict):
    #email table
    email_query = """
        INSERT INTO emails_table (senderName, senderEmail, subject, body)
        VALUES (?, ?, ?, ?)
    """
    email_payload = (
        payload.get("senderName",""),
        payload.get("senderEmail",""),
        payload.get("subject",""),
        payload.get("body","")
    )

    cursor.execute(email_query,email_payload)
    new_email_id = cursor.lastrowid

    #Attachments table
    attachments_query = """
        INSERT INTO attachments_table (emailID, attachmentName, attachmentExtension)
        VALUES (?, ?, ?)
    """
    for attachment in payload.get("attachments",[]):
        seperation_dict = utility.extension_splitter(attachment)
        attachments_payload = (
            new_email_id,
            seperation_dict.get("name",""),
            seperation_dict.get("extension","")
        )
        cursor.execute(attachments_query,attachments_payload)

    analysis_payload_request = payload.get("analysisReturn",{})

    analysis_query = """
        INSERT INTO analysis_feedback (emailID, userAccuracyResponse, serverVersion, phishingScore, phishingType, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    analysis_payload = (
        new_email_id,
        payload.get("accuracy",False),
        VERSION,
        analysis_payload_request.get("score"),
        analysis_payload_request.get("threatLevel"),
        analysis_payload_request.get("reason")
    )
    cursor.execute(analysis_query,analysis_payload)

    new_submission_id = cursor.lastrowid

    test_query = """
        INSERT INTO tests_table (submissionID, testScore, testWeight, testName, testPassed)
        VALUES (?, ?, ?, ?, ?)
    """
    for test in analysis_payload_request.get("passedTests",[]):
        test_payload = (
            new_submission_id,
            test.get("testScore"),
            test.get("testWeight"),
            test.get("testName"),
            True
        )
        cursor.execute(test_query,test_payload)

    for test in analysis_payload_request.get("failedTests",[]):
        test_payload = (
            new_submission_id,
            test.get("testScore"),
            test.get("testWeight"),
            test.get("testName"),
            False
        )
        cursor.execute(test_query,test_payload)

    conn.commit()

def upload_suspicious_actor(conn, cursor, actorName, actorScore):
    #check for existence

