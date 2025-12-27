from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import ops_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UI Mount
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# Router
app.include_router(ops_router.router, prefix="/api/v1/ops", tags=["ops"])

@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "agent": "DevOps Engineer",
        "cloud": settings.GOOGLE_CLOUD_PROJECT
    }

if __name__ == "__main__":
    import uvicorn
    print("DevOps Engineer AI Agent is starting...")
    print("Listening on http://127.0.0.1:8050/ui")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8050, reload=True)