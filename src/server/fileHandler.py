from server import utility
from server.utility import VERSION, CURRENT_DIR
import os

# change directory to the same as the file
FEEDBACK_FILE_PATH = os.path.join(CURRENT_DIR, "feedback.txt")





#silly text writing
def write_feedback(feedback:str):

    with open(FEEDBACK_FILE_PATH,"a+") as feedbackFile:
        feedbackFile.write(utility.get_time() + "\n" + feedback + "\n\n")

        feedbackFile.close()
    
    return


#sql
def create_if_nonexistent(conn, cursor):
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
    """) # actor name will either be an email or a link
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
        
        FOREIGN KEY (emailID) REFERENCES emails_table(emailID) ON DELETE CASCADE
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
        
        FOREIGN KEY (emailID) REFERENCES emails_table(emailID) ON DELETE CASCADE
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
        
        FOREIGN KEY (submissionID) REFERENCES analysis_feedback(submissionID) ON DELETE CASCADE
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

def upload_suspicious_actor(conn, cursor, actorName, actorType, actorScore):
    #check for existence
    cursor.execute("SELECT actorID, suspicionLevel FROM suspicious_actors WHERE (actorName, actorType) = (?, ?)", (actorName, actorType))
    result = cursor.fetchone()

    if not result: # doesnt exist yet
        insert_query = """
            INSERT INTO suspicious_actors (actorName, actorType, suspicionLevel, occurrences, manualConfirmation)
            VALUES (?, ?, ?, ?, ?)
        """
        insert_payload = (
            actorName,
            actorType,
            actorScore,
            1,
            False
        )
        cursor.execute(insert_query,insert_payload)
        conn.commit()
        return
    
    update_query = """
    UPDATE suspicious_actors
    SET occurrences = occurrences + 1, suspicionLevel = ?
    WHERE actorID = ?
    """
    current_score = result[1] if result[1] is not None else 50 # safety
    new_average_score = round((current_score + actorScore) / 2) # more weight for recent events as opposed to a true average
    update_payload = (
        new_average_score,
        result[0]
    )
    cursor.execute(update_query,update_payload)

    conn.commit()

def lookup_suspicious_actor(conn, cursor, actorName, actorType):
    cursor.execute("SELECT suspicionLevel FROM suspicious_actors WHERE (actorName, actorType) = (?, ?)", (actorName, actorType))
    result = cursor.fetchone()

    if not result:
        return 0
    else:
        return result[0]