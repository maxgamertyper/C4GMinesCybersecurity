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
    phishingReason: str = Field(description="A brief, yet thorough explanation of why this conclusion was reached.")
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