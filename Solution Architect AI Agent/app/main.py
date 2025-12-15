from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.services.google_ai import init_vertex_ai

# Lifespan event to initialize Cloud connections on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_vertex_ai()
    yield
    # Shutdown logic (if any)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Frontend
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "agent": "Solution Architect",
        "reasoning_engine": "Vertex AI (Cloud)",
        "mode": "Lightweight Client"
    }

if __name__ == "__main__":
    import uvicorn
    # Running on port 8001 to distinguish from PM Agent
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)