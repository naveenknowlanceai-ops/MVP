from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import agent

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Frontend
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# Mount Evidence (Screenshots)
app.mount("/sandbox", StaticFiles(directory="sandbox"), name="sandbox")

# Register Router
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])

@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "agent": "QA Engineer", 
        "sandbox": settings.SANDBOX_PATH
    }

if __name__ == "__main__":
    import uvicorn
    # PORT 8040 for QA Agent
    uvicorn.run("app.main:app", host="127.0.0.1", port=8040, reload=True)
