import subprocess
import shlex
import os
from langchain_core.tools import tool
from app.core.config import settings

@tool
def run_shell_command(command: str) -> str:
    """
    Executes a terminal command inside the workspace.
    Useful for running scripts (e.g., 'python script.py') or installing packages.
    """
    # 1. Safety Check: Block dangerous commands
    forbidden = ["rm -rf", "sudo", "format", "shutdown", "reboot"]
    if any(bad in command for bad in forbidden):
        return "ERROR: Command Blocked for Safety."

    try:
        # 2. Execute in Sandbox
        # shlex.split helps parse 'python "my script.py"' correctly
        args = shlex.split(command)
        
        result = subprocess.run(
            args,
            cwd=settings.ABS_SANDBOX_PATH, # Force execution in sandbox
            capture_output=True,
            text=True,
            timeout=10 # Prevent infinite loops
        )
        
        # 3. Format Output
        output = result.stdout
        error = result.stderr
        
        if result.returncode == 0:
            return f"EXIT 0 (Success):\n{output}"
        else:
            return f"EXIT {result.returncode} (Error):\n{output}\nSTDERR:\n{error}"

    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out (Limit: 10s)."
    except Exception as e:
        return f"ERROR: Execution failed: {str(e)}"