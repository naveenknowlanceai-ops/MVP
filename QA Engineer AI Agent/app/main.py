from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Serve Frontend (The Coworking Interface)
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# 3. Serve Evidence (Screenshots/Logs from Sandbox)
app.mount("/evidence", StaticFiles(directory="sandbox/screenshots"), name="evidence")

# 4. Health Check
@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "role": "QA Engineer", 
        "modules": ["Vision", "Automation", "Reporting"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True) 
    # Note: Using Port 8001 to avoid conflict with PM Agent (8000)