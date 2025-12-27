import os
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
def list_files():
    """Returns a tree structure of the sandbox."""
    sandbox_root = settings.ABS_SANDBOX_PATH
    file_structure = []

    if not os.path.exists(sandbox_root):
        return {"error": "Sandbox not found", "files": []}

    try:
        # Walk through the directory
        for root, dirs, files in os.walk(sandbox_root):
            # Calculate relative depth to show hierarchy
            rel_path = os.path.relpath(root, sandbox_root)
            
            if rel_path == ".":
                level_name = "ROOT"
            else:
                level_name = rel_path
            
            # Add Folder
            if rel_path != ".":
                 file_structure.append({"name": os.path.basename(root) + "/", "type": "folder", "path": rel_path})

            # Add Files
            for file in files:
                # Store full relative path for clicking later
                full_path = os.path.join(rel_path, file) if rel_path != "." else file
                file_structure.append({"name": file, "type": "file", "path": full_path})
                
        return {"files": file_structure}
    except Exception as e:
        return {"error": str(e), "files": []}

@router.get("/content")
def get_file_content(path: str):
    """Reads a specific file for the UI editor."""
    safe_path = os.path.abspath(os.path.join(settings.ABS_SANDBOX_PATH, path))
    if not safe_path.startswith(settings.ABS_SANDBOX_PATH):
        return {"error": "Access Denied"}
    
    if os.path.exists(safe_path):
        with open(safe_path, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    return {"error": "File not found"}