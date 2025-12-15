from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import the new router
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

# --- REGISTER ROUTERS ---
app.include_router(agent.router, prefix="/api/v1/agent", tags=["agent"])

@app.get("/health")
def health_check():
    return {"status": "active", "system": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)