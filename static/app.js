/* Core Lattice x Alexa demo client.
   Typed input -> POST /api/chat. Web Speech API for voice in/out (bonus). */

const chat = document.getElementById("chat");
const chipsBox = document.getElementById("chips");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const ring = document.getElementById("ring");
const statusLine = document.getElementById("status-line");

const sessionId = "sess-" + Math.random().toString(36).slice(2, 10);

function setRing(state, label) {
  ring.className = state;
  if (label) statusLine.textContent = label;
}

function addMsg(text, who, intent) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  div.textContent = text;
  if (who === "ai" && intent) {
    const tag = document.createElement("span");
    tag.className = "intent";
    tag.textContent = "intent: " + intent;
    div.appendChild(tag);
  }
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function setChips(suggestions) {
  chipsBox.innerHTML = "";
  (suggestions || []).forEach((s) => {
    const b = document.createElement("button");
    b.className = "chip";
    b.textContent = s;
    b.onclick = () => { input.value = s; send(); };
    chipsBox.appendChild(b);
  });
}

async function send(text) {
  const utterance = (text !== undefined ? text : input.value).trim();
  if (!utterance) return;
  input.value = "";
  addMsg(utterance, "user");
  setRing("thinking", "Core Lattice is thinking…");
  const typing = addMsg("…", "ai typing");

  let data;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ utterance, session_id: sessionId }),
    });
    data = await res.json();
  } catch (e) {
    data = { text: "Couldn't reach the Core Lattice engine. Is the server running?", intent: "error" };
  }
  typing.remove();
  addMsg(data.text, "ai", data.intent);
  setChips(data.suggestions);
  setRing("idle", "Tap the mic or type below");
  speak(data.text);
}

sendBtn.onclick = () => send();
input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });

/* ---------------- Voice: speech in (recognition) + speech out (synthesis) */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let recog = null, listening = false;

function speak(text) {
  try {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    // Keep spoken output short: first 280 chars so the demo doesn't drone.
    const short = text.length > 280 ? text.slice(0, 280) + "…" : text;
    const u = new SpeechSynthesisUtterance(short);
    u.onstart = () => setRing("speaking", "Speaking…");
    u.onend = () => { if (!listening) setRing("idle", "Tap the mic or type below"); };
    window.speechSynthesis.speak(u);
  } catch (e) { /* voice-out is a bonus; never break the demo */ }
}

micBtn.onclick = () => {
  if (!SR) {
    statusLine.textContent = "Voice input isn't supported in this browser — type instead.";
    return;
  }
  if (listening) { recog.stop(); return; }
  recog = new SR();
  recog.lang = "en-US";
  recog.interimResults = false;
  recog.onstart = () => { listening = true; micBtn.classList.add("live"); setRing("listening", "Listening… speak now"); };
  recog.onend = () => { listening = false; micBtn.classList.remove("live"); setRing("idle", "Tap the mic or type below"); };
  recog.onerror = (e) => { statusLine.textContent = "Mic error: " + e.error + " — type instead."; };
  recog.onresult = (e) => {
    const said = e.results[0][0].transcript;
    statusLine.textContent = 'Heard: "' + said + '"';
    send(said);
  };
  try { recog.start(); } catch (e) { statusLine.textContent = "Couldn't start the mic — type instead."; }
};

/* Greeting on load */
window.addEventListener("load", () => {
  setTimeout(() => send("hello"), 600);
});
