# 🍣 Sushi - Phishing Detector

Built for the 2026 C4G internship at the Colorado School of Mines as Team 5 (Cybersecurity)

**the "Phishermen"**:

**Front-End team**: "frozenpineapplesoda" and "SamuelMcCaskill"

**Back-End team**: "maxgamertyper" and "angellahao"

**Problem Statement -** With the rise of generative AI, the Phishermen saw a dangerous shift toward highly convincing, automated phishing emails designed to steal credentials or financial information from vulnerable people. To prevent this, we designed **"Sushi"**, a phishing detector that aims to warn people about potential scams before they happen. By making "Sushi" completely **non-blocking**, all normal email interactions are available to the user while delivering instant visual alerts to keep users informed.



**Sushi** - A lightweight browser extension designed to analyze emails using embedded URLs, attachments, and text.

By analyzing the age, entropy, and behavior of links, the extensions and names of attachments, and the urgency of the email, a suspicion score is calculated to alert users of emails that are potentially phishing.



**📖 Quick Links:**
* [Features](#-features)
* [Future Roadmap](#️-future-roadmap)
* [Architecture & Design](#-architecture--design)
* [Installation](#️-installation)
* [Unit Tests](#-unit-tests)
* [Disclaimer](#-disclaimer)

---


## 📄 Features

### Front-End

* **Automatic Email Scraping**: Zero user input is needed to get the contents of the email and send it to the server for analysis
* **Dynamic Alerts**: An analysis returning a bad alert showing that an email is likely phishing will display red, versus an email that is potentially phishing is yellow, or that a safe email is green
* **Email Detection**: Detects if an email is opened or closed and automatically shows or hides analysis results for an email
* **Tailored Layout Spacing**: By using extensive visual alignment testing, a beautifully curated UI was created with detailed margins, padding, and colors to ensure an easy user experience and understanding


### Back-End

* **Redirect Chain Tracking**: Tracks the full path a URL takes a user (`Site A -> Site B -> Site C`) to catch hidden destinations or anti-analysis loops (`Site A -> Site B -> Site C -> Site A -> ...`)
* **Domain Age Analysis**: Queries WHOIS data to evaluate how recently a domain was registered
* **Shannon Entropy Scoring**: Identifies random or algorithmically generated domains commonly used in phishing attempts
* **Database Tracking**: Uses timestamps to track phishing blasts and (logarithmically) increases suspicion when multiple occurrences of a suspicious email occur.
* **Data Storage**: No user data is stored unless an accuracy rating is submitted to ensure user privacy while building a better system
* **Non-Linear Scoring**: One score does not determine the safety of the entire email; all scores are weighted and combined to build an overall safety score.

---

## 🗺️ Future Roadmap

If given more development time, the next phases for **Sushi** would include:
* **Machine Learning Integration:** Integrating small, local Models to dynamically change the weight of tests during analysis upon detection of a phishing campaign and new social engineering tactics.
* **Cross-Client Support:** Expanding the content script injection layer to support Outlook Web App (OWA) and Apple Mail.
* **Universal Threat Database** Allowing users to opt-in to sharing malicious links globally to help all **Sushi** users detect malware and social engineering campaigns.

---

## 🧩 Architecture & Design

> Note: names and directories in this section are clickable to open images or directories

### Early Design

To view our early design planning, technical user flows, and database schemas, please visit the [`/docs`](./docs) directory.

* 🖥️ [**Front-End Userflow Chart**](./docs/UserFlow.png) — Detailed mapping of how the user interacts with Gmail, the extension, and the server (*by SamuelMcCaskill*)
* 🖥️ [**Front-End Mock Up**](./docs/MockExtensionPopup.png) — Simplistic clone of Gmail showing the extension popping up, displaying a warning about a "suspicious" email (*by maxgamertyper*)
* 🗄️ [**Back-End Database Schema**](./docs/DatabaseSchema.png) — Simple diagram showing the different tables and how they link to each other (*by maxgamertyper*)
* 🗄️ [**System Architecture Diagram**](./docs/SystemArchitectureDiagram.png) — Simple diagram showing how the extension and the server talk to one another (*by angellahao*)


### Current Display
* [**Safe Result**](./docs/safeSushiResult.png) — sample result that shows all tests passed and returned a score of 0
* [**Potentially Phishing Result**](./docs/potentialSushiResult.png) — sample result that shows some tests failed and returns a score of 50
* [**Likely Phishing Result**](./docs/phishingSushiResult.png) — sample result that shows all tests failed and returns a score of 100
* [**Example Usage Video**](https://www.youtube.com/watch?v=0CGIPyjGfcw)  — YouTube video that shows installation and examples of multiple features (not all)

### Tech-Stack

* **Front-End:** Vanilla JavaScript (ES6+), HTML5, CSS3, Chrome Extensions API v3
* **Back-End API:** Python 3.14, FastAPI
* **Data & Logic:** Shannon Entropy Algorithms, Live WHOIS Parsing APIs, SQLite, OpenAI library, URL parsing libraries

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
7. Change your base directory to the local repository `cd {your_file_location}`
8. Run `pip install -r requirements.txt` for your Python version
9. Run `fastapi dev ./src/server/main.py` to start the server
10. Go to "mail.google.com" and open an email to see the extension work its magic


---


## 🔒 Unit Tests

To ensure correct operation, this project comes packed with unit tests in the `./src/server/tests` folder.

> Note: all test files will only run if you explicitly call them to prevent any issues *`if __name__ == "__main__"`*

To test the functions of the endpoint, run the `tests/requestTests.py` file
To test the functions of the database, run the `tests/databaseTests.py` file
To test the email analysis functions, run the `tests/testUnitTests.py` file


---

## 📝 Disclaimer

This tool is not professional and was built as part of the C4G@CSM for educational learning purposes.

This tool does not prevent interactions with malicious links or attachments; it only gives a warning signal based on mathematical calculations and heuristics.