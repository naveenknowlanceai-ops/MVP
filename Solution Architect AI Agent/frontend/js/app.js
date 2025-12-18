const API = "http://localhost:8000/api/v1/architect/design";
const sendBtn = document.getElementById('send-btn');
const input = document.getElementById('user-input');
const editor = document.getElementById('design-editor');
const history = document.getElementById('chat-history');

// Check Health
fetch('http://localhost:8000/health')
    .then(r => r.json())
    .then(d => document.getElementById('sys-status').innerText = "Online")
    .catch(e => document.getElementById('sys-status').innerText = "Offline");

sendBtn.onclick = async () => {
    const text = input.value;
    const currentDoc = editor.value;
    if(!text) return;

    addMsg("User", text);
    input.value = "";
    sendBtn.innerText = "Architecting...";
    sendBtn.disabled = true;

    try {
        const res = await fetch(API, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                request: text,
                current_design: currentDoc,
                feedback: currentDoc.length > 5 ? text : ""
            })
        });
        const data = await res.json();
        editor.value = data.design_doc;
        addMsg("Agent", "Design Updated.");
    } catch(e) {
        addMsg("Error", "Failed to connect.");
        console.error(e);
    }
    
    sendBtn.innerText = "DESIGN";
    sendBtn.disabled = false;
};

function addMsg(role, text) {
    const d = document.createElement('div');
    d.className = `message msg-${role.toLowerCase()}`;
    d.innerText = `${role}: ${text}`;
    history.appendChild(d);
}