import os
from langchain_core.tools import tool
from app.core.config import settings

def _is_safe(path: str) -> bool:
    """Security Check: Prevent agent from escaping sandbox."""
    abs_path = os.path.abspath(os.path.join(settings.ABS_SANDBOX_PATH, path))
    return abs_path.startswith(settings.ABS_SANDBOX_PATH)

@tool
def list_files(path: str = ".") -> str:
    """List files in the current directory of the workspace."""
    if not _is_safe(path): return "ACCESS DENIED: Outside Sandbox"
    
    target = os.path.join(settings.ABS_SANDBOX_PATH, path)
    if not os.path.exists(target): return "Directory not found."
    
    try:
        items = os.listdir(target)
        return "\n".join([f"📁 {x}/" if os.path.isdir(os.path.join(target, x)) else f"📄 {x}" for x in items])
    except Exception as e:
        return f"Error: {e}"

@tool
def read_file(file_path: str) -> str:
    """Read the contents of a specific file."""
    if not _is_safe(file_path): return "ACCESS DENIED: Outside Sandbox"
    
    target = os.path.join(settings.ABS_SANDBOX_PATH, file_path)
    if not os.path.exists(target): return "File not found."
    
    try:
        with open(target, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write code/text to a file. Overwrites if exists."""
    if not _is_safe(file_path): return "ACCESS DENIED: Outside Sandbox"
    
    target = os.path.join(settings.ABS_SANDBOX_PATH, file_path)
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error: {e}"

# Export list for binding
dev_tools = [list_files, read_file, write_file]