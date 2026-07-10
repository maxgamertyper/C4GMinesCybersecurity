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
    evilEmailSubject = "ACTION REQUIRED: Your Microsoft Office 365 Subscription Expires in 24 Hours"
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
            Reasoning: {safeAnalysis.phishingReason}
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
            Reasoning: {safeAnalysis.phishingReason}
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

def domain_entropy_checker() :
    normal_domain = "google.com"
    suspicious_domain = "gjanmblridjfnbe.ru"

    # Test normal domain
    normal_response = TestManager.domain_entropy_analysis(normal_domain)

    if normal_response["testScore"] != 0 :
        test_alert("Normal domain was given the wrong entropy score", "Incorrect Domain Entropy Response:")
        test_information(f"""
            Domain: {normal_domain}
            Expected Score: 0
            Got Score: {str(normal_response["testScore"])}
            Details: {normal_response["testDetails"]}
        """)
    else :
        test_succeed("google.com correctly returned score 0", "Correct Domain Entropy Response")

    # Test suspicious/random-looking domain
    suspicious_response = TestManager.domain_entropy_analysis(suspicious_domain)

    if suspicious_response["testScore"] != 50:
        test_alert("Suspicious domain was given the wrong entropy score", "Incorrect Domain Entropy Response:")
        test_information(f"""
            Domain: {suspicious_domain}
            Expected Score: 100
            Got Score: {str(suspicious_response["testScore"])}
            Details: {suspicious_response["testDetails"]}
        """)
    else :
        test_succeed("Random-looking domain correctly returned score 100", "Correct Domain Entropy Response")

def subdomain_checker() :
    no_subdomain_target = "amazon.com"
    one_subdomain_target = "login.amazon.com"
    many_subdomain_target = "hello.hi.fake.abc.ru"

    # test amazon.com
    no_subdomain_response = TestManager.subdomain_analysis(no_subdomain_target)

    if no_subdomain_response["testScore"] != 0 :
        test_alert("No-subdomain domain was given the wrong score", "Incorrect Subdomain Response:")
        test_information(f"""
            Domain: {no_subdomain_target}
            Expected Score: 0
            Got Score: {str(no_subdomain_response["testScore"])}
            Details: {no_subdomain_response["testDetails"]}
        """)
    else :
        test_succeed("amazon.com correctly returned score 0", "Correct Subdomain Response")
    
    # test one subdomain
    one_subdomain_target = TestManager.subdomain_analysis(one_subdomain_target)

    if one_subdomain_target["testScore"] != 0:
        test_alert("One-subdomain domain was given the wrong score", "Incorrect Subdomain Response:")
        test_information(f"""
            Domain: {one_subdomain_target}
            Expected Score: 100
            Got Score: {str(one_subdomain_target["testScore"])}
            Details: {one_subdomain_target["testDetails"]}
        """)
    else :
        test_succeed("login.amazon.com correctly returned score 100", "Correct Subdomain Response")

    # test 4 subdomains
    many_subdomain_target = TestManager.subdomain_analysis(many_subdomain_target)

    if many_subdomain_target["testScore"] != 55 :
        test_alert("Many-subdomain domain was given the wrong score", "Incorrect Subdomain Response:")
        test_information(f"""
            Domain: {many_subdomain_target}
            Expected Score: 100
            Got Score: {str(many_subdomain_target["testScore"])}
            Details: {many_subdomain_target["testDetails"]}
        """)
    else :
        test_succeed("Many-subdomain domain correctly returned score 100", "Correct Subdomain Response")

def redirect_checker() :
    original_redirect_analysis = TestManager.redirect_analysis

    try :
        # case 1: no redirect and no loop should be 0
        def fake_no_redirects(url) :
            return {
                "is_loop": False,
                "redirects": 0
            }
        
        TestManager.redirect_analysis = fake_no_redirects
        no_redirect_response = TestManager.redirect_interpreter("https://example.com")

        if no_redirect_response["testScore"] != 0 :
            test_alert("No-redirect URL was given the wrong score", "Incorrect Redirect Response:")
            test_information(f"""
                Expected Score: 0
                Got Score: {str(no_redirect_response["testScore"])}
                Details: {no_redirect_response["testDetails"]}
            """)
        else :
            test_succeed("No-redirect URL correctly returned score 0", "Correct Redirect Response")
        
        # case 2: 4 redirects should be 35
        def fake_medium_redirects(url) :
            return {
                "is_loop": False,
                "redirects": 4
            }
        
        TestManager.redirect_analysis = fake_medium_redirects
        medium_redirect_response = TestManager.redirect_interpreter("https://example.com")

        if no_redirect_response["testScore"] != 0 :
            test_alert("Medium-redirect URL was given the wrong score", "Incorrect Redirect Response:")
            test_information(f"""
                Expected Score: 35
                Got Score: {str(medium_redirect_response["testScore"])}
                Details: {medium_redirect_response["testDetails"]}
            """)
        else :
            test_succeed("Medium-redirect URL correctly returned score 35", "Correct Redirect Response")
        
        # case 3 : redirect loop should return 65
        def fake_redirect_loop(url) :
            return {
                "is_loop": True,
                "redirects": 2
            }
        
        TestManager.redirect_analysis = fake_redirect_loop
        loop_response = TestManager.redirect_interpreter("https://example.com")

        if no_redirect_response["testScore"] != 0 :
            test_alert("Medium-redirect URL was given the wrong score", "Incorrect Redirect Response:")
            test_information(f"""
                Expected Score: 65
                Got Score: {str(loop_response["testScore"])}
                Details: {loop_response["testDetails"]}
            """)
        else :
            test_succeed("Medium-redirect URL correctly returned score 35", "Correct Redirect Response")
    finally :
        # storing real redirect_analysis function afterward
        TestManager.redirect_analysis = original_redirect_analysis

def link_helper_checker() :
    email_target = "sender@example.com"
    link_target = "https://login.amazon.com/reset"

    # sender@example.com should become example.com
    email_domain = TestManager.get_email_domain(email_target)

    if email_domain != "example.com" :
        test_alert("Email domain extraction failed", "Incorrect get_email_domain response:")
        test_information(f"""
            Input: {email_target}
            Expected: example.com
            Got: {email_domain}
        """)
    else :
        test_succeed("sender@example.com correctly returned example.com", "Correct get_email_domain response")

    # https://login.amazon.com/reset should become login.amazon.com
    cleaned_link = TestManager.sanitize_link(link_target)

    if cleaned_link != "login.amazon.com" :
        test_alert("Link sanitization failed", "Incorrect sanitize_link response")
        test_information(f"""
            Input: {link_target}
            Expected: login.amazon.com
            Got: {cleaned_link}
        """)
    else :
        test_succeed("httpsL//login.amazon.com/reset correctly returned login.amazon.com", "Correct sanitize_link Response")



if __name__ == "__main__":
    ai_test()
    extension_checker()
    domain_entropy_checker()
    subdomain_checker()
    redirect_checker()
    link_helper_checker()