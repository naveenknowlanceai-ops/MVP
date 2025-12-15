from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 1. Security & CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten this in Prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount The Ops Console
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# 3. System Diagnostics (Health Check)
@app.get("/health")
def system_diagnostics():
    return {
        "entity": "DevOps_Engineer_AI_Agent",
        "status": "ONLINE",
        "hardware": "RTX 5060 Ti [DETECTED]",
        "cloud_connection": "Ready",
        "mode": "COWORKING (INTERCEPT ACTIVE)"
    }

# 4. Neural Link (Websocket) - The "Thought Stream"
@app.websocket("/ws/thoughts")
async def thought_stream(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("SYSTEM: Neural Link Established. Awaiting infrastructure mission...")
    try:
        while True:
            data = await websocket.receive_text()
            # This is where we will route commands to LangGraph later
            await websocket.send_text(f"AGENT: Acknowledged '{data}'. Analyzing context...")
    except Exception as e:
        print(f"Link severed: {e}")

if __name__ == "__main__":
    import uvicorn
    print(f"--- DEPLOYING {settings.PROJECT_NAME} ---")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)