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
    returnPayload = {
        "score": -1,
        "threatLevel": "placeholder",
        "reason": "This is a placeholder.",
        "passedTests": [],
        "failedTests": [],
    }

    #attachments
    if payload["attachments"]:
        extensionAnalysis = file_extension_check(payload["attachments"])

    #Full analysis
    AIanalysis = ai.request_ai_analysis(payload["subject"], payload["body"], payload["attachments"])
    AIresults = {
        "testName": "ai_analysis",
        "testPassed": not AIanalysis.is_phishing,
        "testScore": round((AIanalysis.confidence/100) * AIanalysis.suspicionScore + .5),
        "testDetails": AIanalysis.phishingReason
    }
    returnPayload["reason"] = AIresults["testDetails"]
    if not AIresults["testDetails"]:
        returnPayload["reason"] = "Email doesn't have any obvious indicators of phishing or malware"

    links = [get_email_domain(payload.get("sender","")), *payload.get("links",[])]

    worst_age_score, worst_subdomain_score, worst_entropy_score, worst_redirect_score = [{"testScore": -1} for _ in range(4)] # make it so that it will be overriden

    isEmailDomain = True
    for link in links:
        domain = sanitize_link(link)
        age_score = domain_age_analysis(domain)
        subdomain_score = subdomain_analysis(domain)
        entropy_score = domain_entropy_analysis(domain)

        if isEmailDomain: # ignore redirect test for the sender domain
            isEmailDomain = False
            redirect_score = {
                "testName": "redirect_analysis",
                "testScore": 0,
                "testPassed": True,
                "testDetails": "Did not analyze Email Domain"
            }
        else:
            redirect_score = redirect_interpreter(link) 

        if age_score["testScore"] > worst_age_score["testScore"]:
            worst_age_score = age_score
        if subdomain_score["testScore"] > worst_subdomain_score["testScore"]:
            worst_subdomain_score = subdomain_score
        if entropy_score["testScore"] > worst_entropy_score["testScore"]:
            worst_entropy_score = entropy_score
        if redirect_score["testScore"] > worst_redirect_score["testScore"]:
                worst_redirect_score = redirect_score

        

    tests = [worst_age_score, worst_subdomain_score, worst_entropy_score, worst_redirect_score, AIresults]

    if payload["attachments"]:
        tests.append(extensionAnalysis)
    

    if payload["attachments"]:
        extensionAnalysis["testWeight"] = 25
        AIresults["testWeight"] = 20
        worst_age_score["testWeight"] = 15
        worst_redirect_score["testWeight"] = 15
        worst_subdomain_score["testWeight"] = 15
        worst_entropy_score["testWeight"] = 5
        #worst_database_score["testWeight"] = 10
    else:
        worst_age_score["testWeight"] = 25
        AIresults["testWeight"] = 20
        worst_redirect_score["testWeight"] = 20
        worst_subdomain_score["testWeight"] = 20
        worst_entropy_score["testWeight"] = 5
        #worst_database_score["testWeight"] = 10

    running_score = 0

    for test in tests:
        if test["testPassed"]:
            returnPayload["passedTests"].append(test)
        else:
            returnPayload["failedTests"].append(test)
        running_score += test["testScore"] * test["testWeight"]/100

    returnPayload["score"] = round(running_score+.5)
    returnPayload["score"] = 100 if returnPayload["score"]>100 else returnPayload["score"] # cap it

    returnPayload["threatLevel"] = "SAFE" if returnPayload["score"] < 40 else "POTENTIALLY PHISHING" if returnPayload["score"] < 70 else "VERY LIKELY PHISHING"

    return returnPayload


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
            "testScore":50,
            "testPassed": False,
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
    scoreMap = {0: 0, 1: 0, 2: 15, 3: 55, 4: 85}
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
            "testPassed": True if count < 3 else False,
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
        
        today = datetime.now(creation_date.tzinfo)
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
            "testName":"domain_age",
            "testScore":100,
            "testPassed": False,
            "testDetails": "Error occured while looking up domain, treating as suspicious"
        }

def redirect_interpreter(intial_url: str):
    resultDict = redirect_analysis(intial_url)
    runningScore = 0

    loopDetected = resultDict.get("is_loop",False)

    if loopDetected==True:
        runningScore+=65 # very suspicious thing to do
    
    if loopDetected==None:
        runningScore+=80 # couldnt access site

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
        "testPassed": runningScore < 50,
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