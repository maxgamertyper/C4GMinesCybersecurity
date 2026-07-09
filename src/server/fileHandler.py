from server import utility
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
        actorName TEXT,
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
        testSuccessful BOOLEAN,
        
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

