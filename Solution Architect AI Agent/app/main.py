from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import architect

from app.routers import integration

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
app.include_router(integration.router, prefix="/api/v1/integration", tags=["integration"])
@app.get("/health")
def health_check():
    return {"status": "active", "agent": "Solution Architect", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    print("Starting Architect Agent...")
    print("Architect Agent Started on http://127.0.0.1:8020/ui")
    # Using Port 8001 for Architect Agent
    uvicorn.run("app.main:app", host="127.0.0.1", port=8020, reload=True)