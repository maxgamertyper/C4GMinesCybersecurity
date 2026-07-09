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
Site Similarity maybe not now, hard to implement with speed on the server
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
    #Full analysis
    AIanalysis = ai.request_ai_analysis(payload["subject"], payload["body"], payload["attachments"])
    
    #attachment analysis
    extensionAnalysis = file_extension_check(payload["attachments"])
    


    links = [get_email_domain(payload.get("sender","")), *payload.get("links",[])]

    for link in links:
        domain = sanitize_link(link)
        age_score = domain_age_analysis(domain)
        subdomain_score = subdomain_analysis(domain)
        entropy_score = domain_entropy_analysis(domain)
        redirect_score = redirect_interpreter(link)



    #TODO: domain analysis, 


# extension check
COMMON_FAKE_TARGETS = {'.pdf', '.docx', '.xlsx', '.pptx', '.jpg', '.png', '.mp4', '.zip'}
POTENTIALLY_MALICIOUS_EXTENSIONS = {'.exe', '.msi', '.bat', '.cmd', '.ps1', '.vbs', '.scr', '.lnk', '.cpl', '.xlsm', '.docm', '.app'}

# attachments
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


# domains
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
        return {
            "testName":"domain_entropy",
            "testScore":0,
            "testPassed": True,
            "testDetails": "low domain entropy, looks normal"
        }
    elif entropy<4.5:
        return {
            "testName":"domain_entropy",
            "testScore":45,
            "testPassed": True,
            "testDetails": "medium domain entropy, slightly suspicious, but could be corporate"
        }
    else:
        return {
            "testName":"domain_entropy",
            "testScore":100,
            "testPassed": False,
            "testDetails": "high domain entropy, very suspicious"
        }

def subdomain_analysis(domain: str):
    scoreMap = {0: 100, 1: 100, 2: 85, 3: 60, 4: 15}
    if not domain:
        return {
            "testName":"subdomain_count",
            "testScore":0,
            "testPassed": True,
            "testDetails": "Recieved empty domain"
        }
    
    ext = tldextract.extract(domain)
    
    if not ext.subdomain:
        return {
            "testName":"subdomain_count",
            "testScore":0,
            "testPassed": True,
            "testDetails": "No subdomain found"
        }
    
    count = len(ext.subdomain.split('.'))
    
    if count>4: # 5 or more subdomains
        return {
            "testName":"subdomain_count",
            "testScore":100,
            "testPassed": False,
            "testDetails": "More than 5 subdomains, likely trying to impersonate"
        }
        
    return {
            "testName":"subdomain_count",
            "testScore": scoreMap[count],
            "testPassed": True,
            "testDetails": "counted " + str(count) + " subdomains"
        }

def domain_age_analysis(domain:str):
    if not domain:
        return {
            "testName":"domain_age",
            "testScore":0,
            "testPassed": True,
            "testDetails": "Empty Domain Recieved"
        }
    
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date

        if not creation_date:
            return {
            "testName":"domain_age",
            "testScore":100,
            "testPassed": False,
            "testDetails": "Unregistered domain, very suspicious"
        }

        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        today = datetime.now()
        ageDays = (today - creation_date).days
        
        if ageDays<7:
            return {
            "testName":"domain_age",
            "testScore":85,
            "testPassed": False,
            "testDetails": "Very new domain, very suspicious"
        }
        elif ageDays<90:
            return {
            "testName":"domain_age",
            "testScore": 50,
            "testPassed": True,
            "testDetails": "Newer domain, but not too new"
        }
        else:
            return {
            "testName":"domain_age",
            "testScore":0,
            "testPassed": True,
            "testDetails": "older domain, likely safe"
        }


    except Exception:
        return {
            "testName": "domain_age",
            "testScore": 100,
            "testPassed": False,
            "testDetails": "Domain age lookup failed, treating as suspicious."
        }

def redirect_interpreter(intial_url: str):
    resultDict = redirect_analysis(intial_url)
    runningScore = 0

    loopDetected = resultDict.get("is_loop",False)

    if loopDetected==True:
        runningScore+=65 # very suspicious thing to do

    redirects = resultDict.get("redirects",0)

    if redirects<=2:
        pass
    elif redirects<=4:
        runningScore+=35
    elif redirects<=7:
        runningScore+=50
    else:
        runningScore+=80

    runningScore = 100 if runningScore > 100 else runningScore

    return {
        "testName": "redirect_analysis",
        "testScore": runningScore,
        "testPassed": runningScore < 65,
        "testDetails": "redirects: " + str(redirects) + ", redirect loop detected: " + str(loopDetected)
    }

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
                        "redirects": redirect_count
                    }

                visited_urls.add(current_url)

                response = requests.get(current_url, headers=header, allow_redirects=False, timeout=3)

                if response.status_code in (301, 302, 303, 307, 308) and 'Location' in response.headers:
                    current_url = response.headers['Location'].lower().strip()
                    redirect_count += 1
                else: # no more redirects
                    return {
                        "is_loop": False,
                        "redirects": redirect_count
                    }
                
            return {
                        "is_loop": False,
                        "redirects": redirect_count,
                    }
    except requests.RequestException:
        return {
                "is_loop": None,
                "redirects": redirect_count,
            }

def sanitize_link(initial_url: str) -> str:
    extracted = tldextract.extract(initial_url)
    
    if extracted.subdomain:
        return f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
    
    return f"{extracted.domain}.{extracted.suffix}"

def get_email_domain(email: str) -> str:
    if "@" in email:
        return email.split("@")[-1].strip().lower()
    return email # Fallback