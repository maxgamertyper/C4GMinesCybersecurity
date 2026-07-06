from server import ai

"""
{
"body":"Hello, this is an accuracy placeholder body",
"sender": "sender@placeholder.com",
"subject": "Placeholder Subject",
"attachments": ["hi.exe","suspicious.xlsx"],
"links": ["https://amaz0n.com","https://amazon.login.secure.dioudg98745.ru"]
}

"""

def return_creator(test_results: dict):
    pass
    # TODO

def run_tests(payload: dict):

    AIanalysis = ai.request_ai_analysis(payload["subject"], payload["body"], payload["attachments"])



