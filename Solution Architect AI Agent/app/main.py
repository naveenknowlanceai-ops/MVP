from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import architect

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

# Register Router
app.include_router(architect.router, prefix="/api/v1/architect", tags=["architect"])

@app.get("/health")
def health_check():
    return {"status": "active", "agent": "Solution Architect", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    # Using Port 8001 for Architect Agent
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)