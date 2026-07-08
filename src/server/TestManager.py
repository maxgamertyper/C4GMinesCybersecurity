from server import ai
import os
from collections import Counter
import math
import tldextract
import whois
from datetime import datetime
from fake_useragent import UserAgent
import requests

ua = UserAgent()
"""
{
"body":"Hello, this is an accuracy placeholder body",
"sender": "sender@placeholder.com",
"subject": "Placeholder Subject",
"attachments": ["hi.exe","suspicious.xlsx"],
"links": ["https://amaz0n.com","https://amazon.login.secure.dioudg98745.ru"]
}

Needed:
Domain tests (apply to the sender and any links in the body)
Site Similarity
Database Search


{
    "testName": "placeholder_test",
    "testScore": 50,
    "testWeight": 1,
    "testPassed": False,
    "testDetails": "Placeholder"
}
"""

def return_creator(test_results: dict):
    pass
    # TODO

def run_tests(payload: dict):

    AIanalysis = ai.request_ai_analysis(payload["subject"], payload["body"], payload["attachments"])
    extensionAnalysis = file_extension_check(payload["attachments"])
    

    #TODO: domain analysis, 


# extension check
COMMON_FAKE_TARGETS = {'.pdf', '.docx', '.xlsx', '.pptx', '.jpg', '.png', '.mp4', '.zip'}
POTENTIALLY_MALICIOUS_EXTENSIONS = {'.exe', '.msi', '.bat', '.cmd', '.ps1', '.vbs', '.scr', '.lnk', '.cpl', '.xlsm', '.docm', '.app'}

def fake_extension_check(attachment: str):
    _, fake_ext = os.path.splitext(attachment) # split into the name and the extension (just the next dot)

    if fake_ext in COMMON_FAKE_TARGETS:
        return True
    return False

def file_extension_check(attachments: list[str]):

    highest_risk_result = {
        "testName": "extension_analysis",
        "testScore": 0,
        "testPassed": True,
        "testDetails": "All attachments cleared static analysis."
    }

    for attachment in attachments:

        file_name = attachment.lower().strip()
        root, real_ext = os.path.splitext(file_name) # split into the name and the extension

        double_extension = fake_extension_check(root)

        if real_ext in POTENTIALLY_MALICIOUS_EXTENSIONS:
            if double_extension:
                return {
                    "testName": "extension_analysis",
                    "testScore": 100,
                    "testPassed": False,
                    "testDetails": "File has a fake extension and is very likely malicious"
                }
            if highest_risk_result["testScore"] < 80:
                highest_risk_result = {
                        "testName": "extension_analysis",
                        "testScore": 80,
                        "testPassed": False,
                        "testDetails": "File extension has high potential to be malicious"
                    }
        
        elif double_extension:
            if highest_risk_result["testScore"] < 40:
                highest_risk_result = {
                    "testName": "extension_analysis",
                    "testScore": 40,
                    "testPassed": False,
                    "testDetails": "deceptive double-extension"
                }

    return highest_risk_result

def domain_entropy_analysis(domain: str):
    if not domain: #if its empty
        return 0.0
    
    frequencies = Counter(domain)
    total_chars = len(domain)

    entropy = 0.0
    for count in frequencies.values():
        probability = count / total_chars
        entropy -= probability * math.log2(probability)

    entropy = round(entropy, 2)

    if entropy<3.5:
        return 0 # relatively normal domain entropy like google or amazon
    elif entropy<4.5:
        return 35 # could be a more random domain or a corporate domain
    else:
        return 90 # very likely to be phishing

    return 

def subdomain_score(domain: str):
    scoreMap = {0: 100, 1: 100, 2: 85, 3: 60, 4: 15}
    if not domain:
        return 0
    
    ext = tldextract.extract(domain)
    
    if not ext.subdomain:
        return 0
    
    count = len(ext.subdomain.split('.'))
    
    if len(count)>4: # 5 or more subdomains
        return 0
        
    return scoreMap[count]

def domain_age_analysis(domain:str):
    if not domain:
        return 100
    
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if not creation_date:
            return 0

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        today = datetime.now()
        ageDays = today - creation_date
        
        if ageDays<4:
            return 15
        elif ageDays<90:
            return 40
        else:
            return 85


    except Exception:
        return 100

def redirect_analysis(initial_url: str):
    header ={
        "User-Agent": ua.random
    }
    visited_urls = set()
    current_url = initial_url.lower().strip()
    redirect_count = 0

    try:
        with requests.Session() as session:

            while redirect_count < 8:
                session.headers.update(header)

                if current_url in visited_urls:
                    return {
                        "is_loop": True,
                        "redirects": redirect_count,
                        "details": ""
                    }

                visited_urls.add(current_url)

                response = requests.get(current_url, headers=header, allow_redirects=False, timeout=3)

                if response.status_code in (301, 302, 303, 307, 308) and 'Location' in response.headers:
                    current_url = response.headers['Location'].lower().strip()
                    redirect_count += 1
                else: # no more redirects
                    return {
                        "is_loop": False,
                        "redirects": redirect_count,
                        "details": ""
                    }
                
            return {
                        "is_loop": False,
                        "redirects": redirect_count,
                        "details": "Max redirect count reached"
                    }
    except requests.RequestException:
        return {
                "is_loop": None,
                "redirects": redirect_count,
                "details": "Network request failed."
            }

