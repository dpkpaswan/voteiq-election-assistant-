/* ============================================================
   VoteIQ — Frontend Application Logic
   Handles API communication, chat UI, mode switching,
   and all user interactions
   ============================================================ */

// ─── CONFIG ───
const API_BASE = "https://voteiq-backend-817820730147.asia-south1.run.app";

// ─── STATE ───
let currentMode = "guide";
let sessionId = localStorage.getItem("voteiq_session") || ("sess_" + Date.now());
let isWaiting = false;

// Persist session
localStorage.setItem("voteiq_session", sessionId);


/* ═══════════════════════════════
   🎬 ONBOARDING
   ═══════════════════════════════ */

function dismissOnboarding() {
    const el = document.getElementById("onboarding");
    el.style.animation = "fadeOut 0.4s ease forwards";
    setTimeout(() => {
        el.style.display = "none";
        document.getElementById("app").style.display = "flex";
        localStorage.setItem("voteiq_onboarded", "true");
        checkBackendHealth();
    }, 400);
}

// Skip onboarding if already seen
window.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("voteiq_onboarded") === "true") {
        document.getElementById("onboarding").style.display = "none";
        document.getElementById("app").style.display = "flex";
        checkBackendHealth();
    }
});


/* ═══════════════════════════════
   ❤️ HEALTH CHECK
   ═══════════════════════════════ */

async function checkBackendHealth() {
    const dot = document.getElementById("status-dot");
    const text = document.getElementById("status-text");

    try {
        const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
            const data = await res.json();
            dot.className = "status-dot online";
            text.textContent = data.ai_enabled ? "AI Online" : "Fallback Mode";
            document.getElementById("connection-status").title = "Backend connected";
        } else {
            throw new Error("Not OK");
        }
    } catch {
        dot.className = "status-dot offline";
        text.textContent = "Offline";
        document.getElementById("connection-status").title = "Backend unreachable";
    }
}

// Re-check every 30s
setInterval(checkBackendHealth, 30000);


/* ═══════════════════════════════
   💬 CHAT LOGIC
   ═══════════════════════════════ */

function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function updateCharCount() {
    const input = document.getElementById("user-input");
    const count = document.getElementById("char-count");
    count.textContent = `${input.value.length}/500`;

    if (input.value.length > 450) {
        count.style.color = "#ef4444";
    } else {
        count.style.color = "";
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (!message || message.length < 3 || isWaiting) return;

    // Add user message
    addMessage("user", message);
    input.value = "";
    updateCharCount();

    // Lock UI
    setWaiting(true);

    // Show typing indicator
    showTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                mode: currentMode
            }),
            signal: AbortSignal.timeout(15000)
        });

        removeTypingIndicator();

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            const errMsg = errData.message || errData.detail || "Something went wrong. Please try again.";
            addMessage("assistant", `⚠️ ${errMsg}`);
            setWaiting(false);
            return;
        }

        const data = await res.json();

        if (data.success && data.data) {
            const d = data.data;

            // Format and display response
            const formattedResponse = formatResponse(d.response);
            addMessage("assistant", formattedResponse, d.follow_up_suggestions);

            // Update sidebar
            updateSuggestions(d.follow_up_suggestions);
            updateSources(d.sources);
        } else {
            addMessage("assistant", "⚠️ Unexpected response format. Please try again.");
        }

    } catch (err) {
        removeTypingIndicator();

        if (err.name === "TimeoutError" || err.name === "AbortError") {
            addMessage("assistant", "⏱️ Request timed out. The server may be busy — please try again.");
        } else {
            addMessage("assistant", "⚠️ Could not reach the server. Make sure the backend is running.");
        }
    }

    setWaiting(false);
}

function useSuggestion(text) {
    const input = document.getElementById("user-input");
    input.value = text;
    updateCharCount();
    sendMessage();
}


/* ═══════════════════════════════
   🧱 MESSAGE RENDERING
   ═══════════════════════════════ */

function addMessage(role, text, suggestions) {
    const chatBox = document.getElementById("chat-messages");

    const msg = document.createElement("div");
    msg.className = `message ${role} fade-in`;

    const avatarHtml = role === "assistant"
        ? `<div class="avatar">🧠</div>`
        : `<div class="avatar">👤</div>`;

    let suggestionsHtml = "";
    if (role === "assistant" && suggestions && suggestions.length > 0) {
        const chips = suggestions.map(s =>
            `<button class="inline-chip" onclick="useSuggestion('${escapeHtml(s)}')">${escapeHtml(s)}</button>`
        ).join("");
        suggestionsHtml = `<div class="inline-suggestions">${chips}</div>`;
    }

    msg.innerHTML = `
        ${avatarHtml}
        <div class="message-content">
            <div class="message-text">${text}</div>
            ${suggestionsHtml}
        </div>
    `;

    chatBox.appendChild(msg);
    scrollToBottom();
}

function showTypingIndicator() {
    const chatBox = document.getElementById("chat-messages");

    const indicator = document.createElement("div");
    indicator.className = "message assistant fade-in";
    indicator.id = "typing-indicator";
    indicator.innerHTML = `
        <div class="avatar">🧠</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

    chatBox.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}

function scrollToBottom() {
    const chatBox = document.getElementById("chat-messages");
    requestAnimationFrame(() => {
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}


/* ═══════════════════════════════
   📝 RESPONSE FORMATTING
   ═══════════════════════════════ */

function formatResponse(text) {
    if (!text) return "";

    // Convert **bold** → <strong>
    text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Convert *italic* → <em>
    text = text.replace(/\*(.+?)\*/g, "<em>$1</em>");

    // Convert \n to <br>
    text = text.replace(/\n/g, "<br>");

    // Convert numbered lists (1. item)
    text = text.replace(/^(\d+)\.\s+(.+?)(<br>|$)/gm, '<span class="list-number">$1.</span> $2<br>');

    // Convert bullet points (- item)
    text = text.replace(/^[-•]\s+(.+?)(<br>|$)/gm, '• $1<br>');

    return text;
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML.replace(/'/g, "\\'");
}


/* ═══════════════════════════════
   📊 SIDEBAR UPDATES
   ═══════════════════════════════ */

function updateSuggestions(suggestions) {
    const card = document.getElementById("suggestions-card");
    const container = document.getElementById("suggestions-container");

    if (!suggestions || suggestions.length === 0) {
        card.style.display = "none";
        return;
    }

    card.style.display = "block";
    container.innerHTML = suggestions.map(s =>
        `<button class="suggestion-chip" onclick="useSuggestion('${escapeHtml(s)}')">${escapeHtml(s)}</button>`
    ).join("");
}

function updateSources(sources) {
    const card = document.getElementById("sources-card");
    const list = document.getElementById("sources-list");

    if (!sources || sources.length === 0) {
        card.style.display = "none";
        return;
    }

    card.style.display = "block";
    list.innerHTML = sources.map(s => `<li>${escapeHtml(s)}</li>`).join("");
}


/* ═══════════════════════════════
   ⚡ MODE SWITCHING
   ═══════════════════════════════ */

function setMode(mode, btn) {
    currentMode = mode;

    // Update active state
    document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");

    // If switching to Timeline or Guide, optionally auto-fetch
    if (mode === "timeline") {
        loadTimeline();
    } else if (mode === "guide") {
        loadSteps();
    }
}

async function loadTimeline() {
    setWaiting(true);
    showTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/timeline`, { signal: AbortSignal.timeout(8000) });
        removeTypingIndicator();

        if (!res.ok) throw new Error("Failed");

        const data = await res.json();

        if (data.success && data.data) {
            let html = `<strong>📅 Election Timeline — India</strong><br><br>`;
            data.data.forEach((item, i) => {
                html += `<strong>${i + 1}. ${escapeHtmlInner(item.event)}</strong><br>`;
                html += `<span style="opacity:0.75">${escapeHtmlInner(item.description)}</span><br><br>`;
            });

            addMessage("assistant", html);
        }
    } catch {
        removeTypingIndicator();
        addMessage("assistant", "⚠️ Could not load timeline. Is the backend running?");
    }

    setWaiting(false);
}

async function loadSteps() {
    setWaiting(true);
    showTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/api/steps`, { signal: AbortSignal.timeout(8000) });
        removeTypingIndicator();

        if (!res.ok) throw new Error("Failed");

        const data = await res.json();

        if (data.success && data.data) {
            let html = `<strong>🧭 Step-by-Step Guides</strong><br><br>`;
            data.data.forEach((step, i) => {
                html += `<strong>${i + 1}. ${escapeHtmlInner(step.title)}</strong><br>`;
                html += `<span style="opacity:0.75">${escapeHtmlInner(step.description)}</span><br>`;
                if (step.estimated_time) {
                    html += `⏱️ ${escapeHtmlInner(step.estimated_time)}<br>`;
                }
                html += `<br>`;
            });

            addMessage("assistant", html);
        }
    } catch {
        removeTypingIndicator();
        addMessage("assistant", "⚠️ Could not load step guides. Is the backend running?");
    }

    setWaiting(false);
}


/* ═══════════════════════════════
   🧹 UTILITIES
   ═══════════════════════════════ */

function setWaiting(state) {
    isWaiting = state;
    const input = document.getElementById("user-input");
    const btn = document.getElementById("btn-send");
    input.disabled = state;
    btn.disabled = state;

    if (!state) {
        input.focus();
    }
}

function clearChat() {
    const chatBox = document.getElementById("chat-messages");

    // Keep only the first welcome message
    while (chatBox.children.length > 1) {
        chatBox.removeChild(chatBox.lastChild);
    }

    // Reset sidebar
    document.getElementById("suggestions-card").style.display = "none";
    document.getElementById("sources-card").style.display = "none";

    // New session
    sessionId = "sess_" + Date.now();
    localStorage.setItem("voteiq_session", sessionId);
}

function toggleSidebar() {
    const panel = document.getElementById("side-panel");
    panel.classList.toggle("open");
}

function escapeHtmlInner(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;");
}

// Close sidebar when clicking outside (mobile)
document.addEventListener("click", (e) => {
    const panel = document.getElementById("side-panel");
    const toggle = document.getElementById("mobile-sidebar-toggle");

    if (panel && panel.classList.contains("open")) {
        if (!panel.contains(e.target) && !toggle.contains(e.target)) {
            panel.classList.remove("open");
        }
    }
});

// Keyboard shortcut: Escape to close sidebar
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        const panel = document.getElementById("side-panel");
        if (panel) panel.classList.remove("open");
    }
});
