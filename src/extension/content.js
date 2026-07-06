(() => {
  const TEST_SCORE = 95;
  const PANEL_ID = "sushi-gmail-panel";
  let lastMessageKey = null;
  let pendingCheck = null;

  const sign = TEST_SCORE > 75 ? "🛑" : TEST_SCORE >= 40 ? "⚠️" : "✅";
  const color = TEST_SCORE > 75 ? "#d93025" : TEST_SCORE >= 40 ? "#f2994a" : "#188038";

  const panelMarkup = `
  <div class="sushi-header">
    <div class="sushi-title">Sushi</div>
    <button class="sushi-close" aria-label="Close">✕</button>
  </div>

  <div class="sushi-score-wrap">
    <div class="sushi-score-circle" style="border-color:${color}">
      <span class="sushi-score">${TEST_SCORE}</span>
      <span class="sushi-score-label">/100</span>
    </div>

    <div class="sushi-status">
      ${sign} ${TEST_SCORE > 75 ? "High Risk" : TEST_SCORE >= 40 ? "Suspicious" : "Safe"}
    </div>
  </div>

  <div class="sushi-card">
    <div class="sushi-card-title">Reasons</div>
    <ul class="sushi-list"></ul>
  </div>

  <div class="sushi-card">
    <div class="sushi-card-title good">Passed Tests</div>
    <ul class="sushi-list"></ul>
  </div>

  <div class="sushi-card">
    <div class="sushi-card-title bad">Failed Tests</div>
    <ul class="sushi-list"></ul>
  </div>

  <div class="sushi-footer">
    <div class="sushi-question sushi-question-purple">
      Does this seem accurate?
    </div>
    <div class="sushi-buttons">
      <button class="sushi-btn safe">Safe</button>
      <button class="sushi-btn danger">Phishing</button>
    </div>
  </div>
`;

const styles = `
#${PANEL_ID} {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 2147483647;
  width: 340px;
  font-family: system-ui, -apple-system, sans-serif;
  color: #e5e7eb;
}

/* MAIN CARD */
#${PANEL_ID} {
  background: #0b1220;
  border: 1px solid #1f2937;
  border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.45);
  overflow: hidden;
}

/* HEADER */
.sushi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #1f2937;
}

.sushi-title {
  font-weight: 700;
  font-size: 16px;
}

.sushi-close {
  background: transparent;
  border: none;
  color: #9ca3af;
  font-size: 18px;
  cursor: pointer;
}

/* SCORE */
.sushi-score-wrap {
  text-align: center;
  padding: 18px;
}

.sushi-score-circle {
  width: 92px;
  height: 92px;
  border-radius: 50%;
  border: 3px solid;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.sushi-score {
  font-size: 22px;
  font-weight: 700;
}

.sushi-score-label {
  font-size: 12px;
  color: #9ca3af;
}

.sushi-status {
  margin-top: 10px;
  font-size: 13px;
  color: #9ca3af;
}

/* CARDS */
.sushi-card {
  margin: 10px 12px;
  padding: 12px;
  background: #0f172a;
  border: 1px solid #1f2937;
  border-radius: 12px;
}

.sushi-card-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.sushi-card-title.good { color: #22c55e; }
.sushi-card-title.bad { color: #ef4444; }

/* LIST */
.sushi-list {
  margin: 0;
  padding-left: 16px;
  font-size: 12px;
  color: #cbd5e1;
}

/* FOOTER */
.sushi-footer {
  padding: 14px;
  border-top: 1px solid #1f2937;
}

.sushi-question {
  font-size: 12px;
  margin-bottom: 10px;
  color: #9ca3af;
}

/* 🔥 ADDED: purple question text */
.sushi-question-purple {
  color: #3273dc !important;
  font-weight: 600;
}

.sushi-buttons {
  display: flex;
  gap: 10px;
}

.sushi-btn {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.sushi-btn.safe {
  background: #16a34a;
  color: white;
}

.sushi-btn.danger {
  background: #dc2626;
  color: white;
}
`;
  
  function scrapeEmailContent() {
    const senderName = document.querySelector(".gD")?.textContent?.trim() || "";
    const senderEmail = document.querySelector(".gD")?.getAttribute("email") || "";
    const subject = document.querySelector(".hP")?.textContent?.trim() || "";
    const body = document.querySelector(".a3s")?.textContent?.trim() || "";
    return { senderName, senderEmail, subject, body };
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
