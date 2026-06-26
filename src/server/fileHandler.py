from server import utility
import os

# change directory to the same as the file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE_PATH = os.path.join(CURRENT_DIR, "feedback.txt")

def write_feedback(feedback:str):

    with open(FEEDBACK_FILE_PATH,"a+") as feedbackFile:
        feedbackFile.write(utility.get_time() + "\n" + feedback)

        feedbackFile.close()
    
    return