// NOTE THE PORT 8001
const API = "http://localhost:8040/api/v1/agent/run";
const sendBtn = document.getElementById('send-btn');
const input = document.getElementById('user-input');
const codeEditor = document.getElementById('code-editor');
const logs = document.getElementById('log-viewer');
const history = document.getElementById('chat-history');

// Check Health
fetch('http://localhost:8040/health')
    .then(r => r.json())
    .then(d => document.getElementById('sys-status').innerText = "Online")
    .catch(e => document.getElementById('sys-status').innerText = "Offline");

sendBtn.onclick = async () => {
    const text = input.value;
    const currentCode = codeEditor.value;
    if(!text) return;

    addMsg("User", text);
    input.value = "";
    sendBtn.innerText = "Designing...";
    sendBtn.disabled = true;

    try {
        const res = await fetch(API, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                requirement: text,
                previous_code: currentCode,
                feedback: currentCode.length > 5 ? text : "" // If code exists, treat text as feedback
            })
        });
        const data = await res.json();
        
        codeEditor.value = data.generated_code;
        logs.innerText = data.logs; // "Code Saved to sandbox..."
        addMsg("Agent", "Test Script Generated and Saved.");
    } catch(e) {
        addMsg("Error", "Connection Failed.");
        console.error(e);
    }

    sendBtn.innerText = "GENERATE TEST";
    sendBtn.disabled = false;
};

function addMsg(role, text) {
    const d = document.createElement('div');
    d.className = `message msg-${role.toLowerCase()}`;
    d.innerText = `${role}: ${text}`;
    history.appendChild(d);
}