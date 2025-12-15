from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 1. CORS - Crucial for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount UI
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# 3. Health & Capability Check
@app.get("/system/status")
def system_check():
    return {
        "status": "operational",
        "agent_role": "Software Developer (Level 3)",
        "sandbox_path": settings.SANDBOX_PATH,
        "mode": "Coworking (Waiting for Human)"
    }

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Developer Agent Online at: http://localhost:8001/ui")
    print(f"📂 Workspace mounted at: {settings.SANDBOX_PATH}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)