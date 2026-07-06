import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
from rich import print

load_dotenv()

token = os.environ["SUSHI_API_KEY"]
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

class PhishingAnalysis(BaseModel):
    is_phishing: bool = Field(description="True if the email is a likely phishing attempt, False if the email is safe.")
    phishingReasons: list[str] = Field(description="A brief, seperated explanation of why this conclusion was reached. ")
    suspicionScore: int = Field(description="A score from 0 to 100 on the suspicion level of this email. 0 being safe and 100 being extremly likely phishing")
    confidence: int = Field(description="A confidence rating from 0 to 100. If the email is clearly safe and has no threats, confidence should be near 100 because you are certain it is safe.")


def request_ai_analysis(subject: str, body: str, attachments: list[str]):
    try:
        response = client.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI model designed to detect phishing. If you deem something as phishing, "
                        "you must state your reasoning and how confident you are in that analysis. Be concise "
                        "in your reasoning and maximize it to 3 major reasons as to why this email is phishing. "
                        "If you deem the email safe, leave no reasoning and set suspicionScore to 0. "
                        "CRITICAL: If an email is completely normal, safe, and lacks any phishing indicators, "
                        "you must be highly confident that it is safe. Set the confidence score close to 100."
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps({
                        "body":body,
                        "subject":subject,
                        "attachments_names":attachments
                        }),
                }
            ],
            temperature=0.1,
            model=model,
            response_format=PhishingAnalysis
        )
        analysis = response.choices[0].message.parsed
        return analysis
    except Exception as e:
        print("[bold red]Out of AI requests[/bold red]")
        return False


# the test
if __name__ == "__main__": #only ran if the actually ran the specific file
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


    safeAnalysis = request_ai_analysis(safeEmailSubject, safeEmailBody, safeEmailAttachments)
    if (safeAnalysis.is_phishing or safeAnalysis.suspicionScore > 70 or safeAnalysis.confidence < 75):
        print("[bold red]Incorrect AI Response:[/bold red] Safe email deemed as suspicious")
        print("Analysis Details: ")
        print("Is Phishing: " + str(safeAnalysis.is_phishing))
        print("Confidence: " + str(safeAnalysis.confidence))
        print("Suspicion Score: " + str(safeAnalysis.suspicionScore))
        print("Reasoning: " + "\n".join(safeAnalysis.phishingReasons))
    else:
        print("[bold green]AI deemed the safe email safe[/bold green]")

    evilAnalysis = request_ai_analysis(evilEmailSubject, evilEmailBody, evilEmailAttachments)
    if (not evilAnalysis.is_phishing or evilAnalysis.suspicionScore < 60 or evilAnalysis.confidence < 75):
        print("[bold red]Incorrect AI Response:[/bold red] Evil email deemed as safe")
        print("Analysis Details: ")
        print("Is Phishing: " + str(evilAnalysis.is_phishing))
        print("Confidence: " + str(evilAnalysis.confidence))
        print("Suspicion Score: " + str(evilAnalysis.suspicionScore))
        print("Reasoning: " + "\n".join(evilAnalysis.phishingReasons))
    else:
        print("[bold green]AI deemed the evil email evil[/bold green]")
