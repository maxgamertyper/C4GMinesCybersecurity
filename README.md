# 🍣 Sushi - Phishing Detector

Built for the 2026 C4G internship at the Colorado School of Mines as Team 5 (Cybersecurity)

**the "Phishermen"**:
**Front-End team**: "frozenpineapplesoda" and "SamuelMcCaskill"
**Back-End team**: "maxgamertyper" and "angellahao"

**Sushi** - A lightweight browser extension designed to analyze emails using embedded URLs, attachments, and text.

By analyzing the age, entropy, and behavior of links; the extensions and names of attachments; and the urgency of the email; A suspicion score is calculated to alert users of emails that are potentially phishing


---


## 📄 Features

### Front-End


### Back-End

* **Redirect Chain Tracking**: Tracks the full path a url takes a user (`Site A -> Site B -> Site C`) to catch hidden destinations or anti-analysis loops (`Site A -> Site B -> Site C -> Site A -> ...`)
* **Domain Age Analysis**: Queries WHOIS data to evaluate how recently a domain was registered
* **Shannon Entropy Scoring**: Identifies random or algorithimically generated domains commonly used in phishing attemps
* **Database Tracking**: Uses timestamps to track phishing blasts and (logarithmically) increases suspicion when multiple occurences of a suspicious email occurs.
* **Data Storage**: No user data is stored unless an accuracy rating is submitted to ensure user privacy while building a better system
* **Non-Linear Scoring**: One score does not determine the safety of the entire email, all scores are weighted and combined to build an overall safety score.

---

## 🛠️ Installation

1. Clone or download this repository to your PC
2. Open your browser and navigate to the extensions page:
   * **Chrome/Edge:** `chrome://extensions/`
   * **Firefox:** `about:debugging`
3. Enable **Developer mode** (usually a toggle in the top-right corner).
4. Click **Load unpacked** and select the folder containing this extension's source code.
5. Install a Python version that supports the packages in `requirements.txt`, it is coded in **Python3.14**
6. Open **VS Code** or a terminal window
7. Change you base directory to the local repository `cd {your_file_location}`
8. Run `pip install -r requirements.txt` for your python version
9. Run `fastapi dev ./src/server/main.py` to start the server
10. Go to "mail.google.com" and open an email to see the extension work its magic


---

## 🔒 Unit Tests

To ensure correct operation, this project comes packed with unit tests in the `./src/server/tests` folder

> Note: all test files will only run if you explicitly call them to prevent any issues *`if __name__ == "__main__"`*

To test the functions of the endpoint, go run the `tests/requestTests.py` file
To test the functions of the database, go run the `tests/databaseTests.py` file
To test the email analysis functions, go run the `tests/testUnitTests.py` file


---

## 📝 Disclaimer

This tool is not professional and was built as part of the C4G@CSM as stated previously.

This tool does not prevent interactions with malicious links or attachments, only gives a warning signal based on mathematical calculations and heuristics.