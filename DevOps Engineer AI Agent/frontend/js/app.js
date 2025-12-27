const API_URL = "http://localhost:8050/api/v1/ops/execute";
const cmdInput = document.getElementById('cmd-input');
const history = document.getElementById('terminal-history');
const editor = document.getElementById('code-editor');

// Init
fetch('http://localhost:8050/health')
    .then(r => r.json())
    .then(d => document.getElementById('sys-status').innerText = "ONLINE")
    .catch(e => document.getElementById('sys-status').innerText = "OFFLINE");

cmdInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const text = cmdInput.value;
        if(!text) return;
        
        log("USER", text);
        cmdInput.value = "";
        
        // Coworking Intercept Check
        const currentCode = editor.value;
        
        log("SYS", "Initializing Agentic Workflow...");
        
        try {
            const res = await fetch(API_URL, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    command: text,
                    current_code: currentCode, // Sending context if intercepting
                    intercept_msg: currentCode.length > 5 ? text : "" // If code exists, treat input as refinement
                })
            });
            const data = await res.json();
            
            // Clean up Markdown blocks for editor
            let cleanCode = data.iac_output.replace(/```hcl|```terraform|```/g, "").trim();
            editor.value = cleanCode;
            log("AGENT", "Architecture Generated.");
            
        } catch(err) {
            log("SYS", "CONNECTION ERROR");
            console.error(err);
        }
    }
});

function log(who, text) {
    const d = document.createElement('div');
    d.className = `log-${who.toLowerCase()}`;
    d.innerHTML = `[${who}] ${text}`;
    history.appendChild(d);
    history.scrollTop = history.scrollHeight;
}