import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import dev_api

# 1. Initialize App
app = FastAPI(title=settings.PROJECT_NAME)
from app.routers import dev_api, files_api  # <--- IMPORT files_api

# 2. CORS (Permissive for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Register Frontend
# This serves your HTML file at /ui/
app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")

# 4. Register Backend Router
# This connects http://localhost:PORT/api/v1/dev/run
print("🔗 Registering API Routers...")
app.include_router(dev_api.router, prefix="/api/v1/dev", tags=["dev"])
print("✅ Router Registered: /api/v1/dev/run")

app.include_router(files_api.router, prefix="/api/v1/files", tags=["files"]) # <--- REGISTER IT
# 5. Health Check
@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "mode": "Developer Agent", 
        "port": "Dynamic"
    }

if __name__ == "__main__":
    import uvicorn
    # Use 8001 by default, but allows flags to override
    uvicorn.run("app.main:app", host="localhost", port=8030, reload=True)