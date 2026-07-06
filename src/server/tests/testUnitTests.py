import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server import ai
from server import TestManager
from rich import print



def test_warning(text:str, head: str):
    print("[bold yellow]" + head + "[/bold yellow]: " + text)

def test_alert(text:str, head: str):
    print("[bold red]" + head + "[/bold red]: " + text)

def test_information(text:str):
    print("[bold]\\[Information][/bold]: " + text)

def test_succeed(text:str, head: str):
    print("[bold green]" + head + "[/bold green]: " + text)



def ai_test():
    evilEmailSubject = "Subject: ACTION REQUIRED: Your Microsoft Office 365 Subscription Expires in 24 Hours"
    evilEmailBody="""
    Dear User,
    This is an automated notification from the Microsoft Billing Team. We have detected that your Office 365 business subscription is scheduled to expire in exactly 24 hours. Failure to verify your account and update your billing information will result in the immediate suspension of your email access, and all stored files on OneDrive will be permanently deleted.
    To avoid service disruption, please verify your account and update your payment details immediately
    Click here to Verify your Microsoft 365 Account
    If you need assistance, contact our billing support team at 1-800-555-0199.
    Sincerely,
    The Microsoft 365 Billing Department
    """
    evilEmailAttachments = ["invoice.pdf.exe", "warning.docx.app"]

    safeEmailBody = "Hi Bill, I hope this message finds you well. I am reaching out to share a quick update on the Q3 marketing deliverables. We have successfully completed the initial draft of the campaign, which is currently attached for your review.To ensure we align on the final steps, I would like to schedule a brief 15-minute sync next week. Would you be available to meet on Tuesday at 10:00 AM or Wednesday at 2:00 PM?Let me know what time works best for your schedule.Best regards,Tom"
    safeEmailSubject = "Project Q3 Update & Meeting Request"
    safeEmailAttachments = ["meetingPlan-Wednesday.docx","Q3Projections.xlsx"]


    safeAnalysis = ai.request_ai_analysis(safeEmailSubject, safeEmailBody, safeEmailAttachments)
    if (safeAnalysis.is_phishing or safeAnalysis.suspicionScore > 70 or safeAnalysis.confidence < 75):
        test_alert("Safe email deemed as suspicious", "Incorrect AI Response:")
        test_information(f"""
            Analysis Details: 
            Is Phishing: {str(safeAnalysis.is_phishing)}
            Confidence: {str(safeAnalysis.confidence)}
            Suspicion Score: {str(safeAnalysis.suspicionScore)}
            Reasoning: {"\n".join(safeAnalysis.phishingReasons)}
        """)
    else:
        test_succeed("", "AI deemed the safe email safe")

    evilAnalysis = ai.request_ai_analysis(evilEmailSubject, evilEmailBody, evilEmailAttachments)
    if (not evilAnalysis.is_phishing or evilAnalysis.suspicionScore < 60 or evilAnalysis.confidence < 75):
        test_alert("Evil email deemed as safe", "Incorrect AI Response:")
        test_information(f"""
            Analysis Details: 
            Is Phishing: {str(evilAnalysis.is_phishing)}
            Confidence: {str(evilAnalysis.confidence)}
            Suspicion Score: {str(evilAnalysis.suspicionScore)}
            Reasoning: {"\n".join(evilAnalysis.phishingReasons)}
        """)
    else:
        test_succeed("", "AI deemed the evil email evil")



def extension_analysis_helper(idealscore: int, failResponse: str, analysis: dict):
    if analysis["testScore"]!=idealscore:
        test_alert(failResponse, "Incorrect Extension Response:")
        test_information(f"""
            Analysis Details: 
            Test Passed: {analysis["testPassed"]}
            Score: {str(analysis["testScore"])}
            Details: {analysis["testDetails"]}
        """)
    else:
        test_succeed(f"{idealscore} was correct in analysis","Correct Extension Response")

def extension_checker():
    double_malicious_target = ["invoiceQ3.docx","invoice.pdf.exe"]
    double_nonmalicious_target = ["passwords.txt","birthdayParty.png.jpg"]
    malicious_target = ["picture.png", "baby.jpg", "game.exe"]
    safe_target = ["picture.png", "baby.jpg", "memo.pdf"]

    dmt_response = TestManager.file_extension_check(double_malicious_target)
    extension_analysis_helper(100,"Double Extension Malicious Files deemed as Safe",dmt_response)

    mt_response = TestManager.file_extension_check(malicious_target)
    extension_analysis_helper(80,"Malicious Files misrepresented",mt_response)


    dnt_response = TestManager.file_extension_check(double_nonmalicious_target)
    extension_analysis_helper(40,"Double Extension Files misrepresented",dnt_response)


    safe_response = TestManager.file_extension_check(safe_target)
    extension_analysis_helper(0,"Safe Files deemed as Malicious",safe_response)





if __name__ == "__main__":
    ai_test()
    extension_checker()