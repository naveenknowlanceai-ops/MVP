// --- CONFIGURATION ---
const API_BASE = "http://localhost:8020/api/v1";
const CHAT_ENDPOINT = `${API_BASE}/architect/design`;
const JIRA_CONNECT_ENDPOINT = `${API_BASE}/integration/jira/connect`;
const CONF_CONNECT_ENDPOINT = `${API_BASE}/integration/confluence/connect`;

// --- DOM ELEMENTS ---
const sendBtn = document.getElementById('send-btn');
const input = document.getElementById('user-input');
const editor = document.getElementById('design-editor');
const historyPanel = document.getElementById('chat-history');
const modal = document.getElementById('config-modal');
const approvalBadge = document.getElementById('approval-badge');
const sysStatus = document.getElementById('sys-status');

// --- STATE ---
let messageHistory = [];

// --- INITIALIZATION ---
// Check Backend Health on Load
fetch('http://localhost:8020/health')
    .then(r => r.json())
    .then(d => {
        sysStatus.innerText = "ONLINE";
        sysStatus.style.color = "#3fb950"; // Green
    })
    .catch(e => {
        sysStatus.innerText = "OFFLINE";
        sysStatus.style.color = "#f85149"; // Red
    });

// --- CHAT LOGIC ---
sendBtn.onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    // 1. UI Updates
    addMsg("User", text);
    input.value = "";
    sendBtn.innerText = "Working...";
    sendBtn.disabled = true;

    try {
        // 2. Send Request to Agent
        const res = await fetch(CHAT_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request: text,
                current_design: editor.value, // Pass current doc context
                message_history: messageHistory
            })
        });

        const data = await res.json();

        // 3. Handle Response
        if (data.design_doc) {
            // Update the Editor
            editor.value = data.design_doc.content || data.design_doc; // Handle object or string
            
            // Render Diagram
            renderDiagram(editor.value);
        }

        // Update History State
        // (If the backend returns the updated history, use it. Otherwise append manually)
        if (data.message_history) {
            messageHistory = data.message_history;
        }

        addMsg("Architect", "Task Complete. Check the Design Doc tab.");

    } catch (e) {
        console.error(e);
        addMsg("System", "❌ Error connecting to Agent.");
    }

    sendBtn.innerText = "EXECUTE";
    sendBtn.disabled = false;
};

// --- HELPER: Add Message to Chat ---
function addMsg(role, text) {
    const d = document.createElement('div');
    d.className = `message msg-${role.toLowerCase()}`;
    d.innerHTML = `<strong>${role}:</strong> ${text}`;
    historyPanel.appendChild(d);
    historyPanel.scrollTop = historyPanel.scrollHeight;
}

// --- HELPER: Render Mermaid Diagram ---
async function renderDiagram(markdownText) {
    // Regex to find ```mermaid ... ``` block
    const mermaidMatch = markdownText.match(/```mermaid([\s\S]*?)```/);
    
    if (mermaidMatch && mermaidMatch[1] && window.mermaid) {
        const graphDefinition = mermaidMatch[1].trim();
        const element = document.getElementById('mermaid-canvas');
        
        // Reset element
        element.removeAttribute('data-processed');
        element.innerHTML = graphDefinition;
        
        try {
            await window.mermaid.run({ nodes: [element] });
            console.log("Diagram Rendered");
        } catch (e) {
            console.error("Mermaid Render Error:", e);
            element.innerHTML = "❌ Error rendering diagram. Check syntax.";
        }
    }
}

// --- TABS LOGIC ---
// Attached to window so HTML buttons can see it
window.showTab = function(name) {
    document.getElementById('design-editor').style.display = name === 'doc' ? 'block' : 'none';
    document.getElementById('diagram-view').style.display = name === 'diagram' ? 'block' : 'none';
    
    // Toggle active button style
    const btns = document.querySelectorAll('.toolbar button');
    btns.forEach(b => b.classList.remove('active-tab'));
    event.target.classList.add('active-tab');
}

// --- ATLASSIAN INTEGRATION LOGIC (THE MISSING PART) ---

// 1. Toggle Modal
window.toggleConfig = function() {
    modal.style.display = modal.style.display === 'none' ? 'block' : 'none';
}

// 2. Connect Logic
window.connectAtlassian = async function() {
    // Get values
    const domain = document.getElementById('conf-domain').value;
    const email = document.getElementById('conf-email').value;
    const token = document.getElementById('conf-token').value;
    const project = document.getElementById('conf-project').value;
    const space = document.getElementById('conf-space').value;
    
    const statusEl = document.getElementById('conf-status');
    statusEl.innerText = "⏳ Connecting...";
    statusEl.style.color = "yellow";

    try {
        // Step A: Connect Jira
        const jiraRes = await fetch(JIRA_CONNECT_ENDPOINT, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                domain: domain, 
                email: email, 
                token: token, 
                project_key: project 
            })
        });

        if (!jiraRes.ok) {
            const err = await jiraRes.json();
            throw new Error("Jira: " + err.detail);
        }

        // Step B: Connect Confluence
        const confRes = await fetch(CONF_CONNECT_ENDPOINT, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                domain: domain, 
                email: email, 
                token: token, 
                space_key: space 
            })
        });

        if (!confRes.ok) {
            throw new Error("Confluence Connection Failed");
        }

        // Success
        statusEl.innerText = "✅ All Systems Connected!";
        statusEl.style.color = "#3fb950";
        
        // Auto-close after 2 seconds
        setTimeout(() => { toggleConfig(); }, 2000);

    } catch (e) {
        statusEl.innerText = "❌ " + e.message;
        statusEl.style.color = "#f85149";
    }
}