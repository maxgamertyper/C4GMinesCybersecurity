(() => {
  const TEST_SCORE = 95;
  const PANEL_ID = "sushi-gmail-panel";
  let lastMessageKey = null;
  let pendingCheck = null;

  const sign = TEST_SCORE > 75 ? "🛑" : TEST_SCORE >= 40 ? "⚠️" : "✅";
  const color = TEST_SCORE > 75 ? "#d93025" : TEST_SCORE >= 40 ? "#f2994a" : "#188038";

  const panelMarkup = `
    <div class="box sushi-panel-card custom-dark-box" style="padding: 14px !important;">
      <div class="container my-3 px-3">
        <h1 class="title has-text-white">Sushi</h1>
      </div>

      <div class="mx-auto">
        <p class="is-size-5 has-text-grey-light m-3">Phishing Detector Score</p>
        <div class="has-text-centered">
          <span class="tag is-small has-text-info">${TEST_SCORE}</span>
          <span class="tag is-dark has-text-white">/ 100</span>
        </div>
      </div>

      <div class="custom-dark-box p-4 my-4">
        <p class="is-size-6 has-text-light mb-2">Reasons:</p>
        <ul class="ml-4">
        </ul>
      </div>

      <div class="custom-dark-box p-4 my-4">
        <p class="is-size-6 mb-2" style="color: #48c78e !important;">Passed Tests:</p>
        <ul class="ml-4">
        </ul>
      </div>

      <div class="custom-dark-box p-4 my-4">
        <p class="is-size-6 mb-2" style="color: #f14668 !important;">Failed Tests:</p>
        <ul class="ml-4">
        </ul>
      </div>

      <div class="box has-text-centered m-3">
        <p class="is-size-6 mb-3" style="color: #485fc7 !important;">Does this seem accurate?</p>
        <div class="is-flex is-justify-content-space-between">
         <button id="yes" class="button is-success" style="width: 48%;">Safe</button>
         <button id="no" class="button is-danger" style="width: 48%;">Phishing</button>
        </div>
      </div>
      <div class="is-flex is-justify-content-space-between is-align-items-center p-3">
        <h1 class="title has-text-white m-0">Sushi</h1>
            <button class="delete sushi-panel-close" aria-label="Close"></button>
      </div>
    </div>
  `;

  const styles = `
    @keyframes sushiPulse {
      0% { box-shadow: 0 0 0 0 ${color}66; }
      70% { box-shadow: 0 0 0 16px rgba(0,0,0,0); }
      100% { box-shadow: 0 0 0 0 rgba(0,0,0,0); }
    }

    #${PANEL_ID} {
      position: fixed;
      right: 20px;
      bottom: 20px;
      z-index: 2147483647;
      width: min(360px, calc(100vw - 24px));
      font-family: Arial, sans-serif;
      color: #f3f4f6;
      pointer-events: auto;
    }

    #${PANEL_ID} .sushi-panel-card {
      background: #111827;
      border: 2px solid ${color};
      border-radius: 16px;
      box-shadow: 0 16px 45px rgba(0, 0, 0, 0.35);
      overflow: hidden;
      animation: sushiPulse 1.4s infinite ease-in-out;
    }

    #${PANEL_ID} .custom-dark-box {
      background: #111827;
      border: 1px solid #374151;
      border-radius: 12px;
    }

    #${PANEL_ID} .box.has-text-centered {
      background: #111827;
      border-color: #374151;
    }

    #${PANEL_ID} .has-text-light {
      color: #d1d5db !important;
    }

    #${PANEL_ID} .has-text-grey-light {
      color: #9ca3af !important;
    }

    #${PANEL_ID} .tag.is-dark {
      background: #0f172a;
      border-color: #374151;
    }

    #${PANEL_ID} .button.is-success,
    #${PANEL_ID} .button.is-danger {
      min-width: 48%;
    }

    #${PANEL_ID} .button.is-success {
      background: #16a34a;
      border-color: transparent;
    }

    #${PANEL_ID} .button.is-danger {
      background: #dc2626;
      border-color: transparent;
    }
  `;
  function scrapeEmailContent() {
    const senderName= document.querySelector (".gD")?.textContent?.trim() || "";
    const senderEmail = document.querySelector(".gD")?.getAttribute("email") || "";
    const subject = document.querySelector(".hP")?.textContent?.trim() || "";
    const body = document.querySelector(".a3s")?.textContent?.trim() || "";
    return { senderName, senderEmail, subject, body };
  }
  async function analyzeEmail(emailData) {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(emailData)
    });
    return await response.json();
  }

  const injectBulma = () => {
    if (document.getElementById("sushi-bulma-styles")) return;
    const link = document.createElement("link");
    link.id = "sushi-bulma-styles";
    link.rel = "stylesheet";
    link.href = chrome.runtime.getURL("popup/bulma.min.css");
    document.head.appendChild(link);
  };

  const ensureStyles = () => {
    injectBulma();
    if (document.getElementById("sushi-gmail-panel-styles")) return;
    const styleTag = document.createElement("style");
    styleTag.id = "sushi-gmail-panel-styles";
    styleTag.textContent = styles;
    document.head.appendChild(styleTag);
  };

  const getMessageKey = () => {
    const thread = document.querySelector("[data-thread-perm-id]");
    const message = document.querySelector("[data-message-id]");
    const subject = document.querySelector("[role='main'] .bog, [role='main'] .hP, [role='main'] .g2")?.textContent?.trim() || "";
    return `${window.location.hash || ""}|${thread?.getAttribute("data-thread-perm-id") || ""}|${message?.getAttribute("data-message-id") || ""}|${subject}`;
  };

  const isEmailOpen = () => {
    const hash = window.location.hash || "";
    const hasMessageHash = /#(?:inbox|draft|label|search|spam|trash|archive|sent)\/[^/]+/i.test(hash);
    const hasThreadView = Boolean(document.querySelector("[role='main'] [data-thread-perm-id], [role='main'] [data-message-id]"));
    const hasMessageBody = Boolean(document.querySelector("[role='main'] .a3s, [role='main'] .ii"));
    return hasMessageHash && (hasThreadView || hasMessageBody);
  };

  const showPanel = () => {
    ensureStyles();

    const existingPanel = document.getElementById(PANEL_ID);
    if (existingPanel) {
      existingPanel.remove();
    }

    const panel = document.createElement("div");
    panel.id = PANEL_ID;
    panel.innerHTML = panelMarkup;
    document.body.appendChild(panel);

    panel.querySelector(".sushi-panel-close").addEventListener("click", () => {
      panel.remove();
    });
  };

  const refreshPanelIfNeeded = () => {
    if (!isEmailOpen()) {
      lastMessageKey = null;
      const existingPanel = document.getElementById(PANEL_ID);
      if (existingPanel) {
        existingPanel.remove();
      }
      return;
    }

    const messageKey = getMessageKey();
    if (messageKey && messageKey !== lastMessageKey) {
      lastMessageKey = messageKey;
      const emailData = scrapeEmailContent();
      console.log(emailData);
      const analysisResult = analyzeEmail(emailData);
      console.log(analysisResult);
      showPanel();
    }
  };

  const scheduleRefresh = () => {
    clearTimeout(pendingCheck);
    pendingCheck = setTimeout(refreshPanelIfNeeded, 400);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", scheduleRefresh, { once: true });
  } else {
    scheduleRefresh();
  }

  const observer = new MutationObserver(() => {
    scheduleRefresh();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
    attributes: true,
  });

  window.addEventListener("hashchange", scheduleRefresh);
  window.addEventListener("popstate", scheduleRefresh);
})();
