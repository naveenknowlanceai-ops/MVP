import os
from langchain_core.tools import tool
from typing import Optional

# SANDBOX PATH (Safety First)
# The agent can only write inside this directory
WORKING_DIRECTORY = "./project_workspace"

if not os.path.exists(WORKING_DIRECTORY):
    os.makedirs(WORKING_DIRECTORY)

@tool
def list_files(directory: Optional[str] = ".") -> str:
    """Lists files in the project workspace to see what exists."""
    path = os.path.join(WORKING_DIRECTORY, directory)
    try:
        files = os.listdir(path)
        return str(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@tool
def create_directory(directory_name: str) -> str:
    """Creates a new folder in the project workspace."""
    path = os.path.join(WORKING_DIRECTORY, directory_name)
    try:
        os.makedirs(path, exist_ok=True)
        return f"Created directory: {directory_name}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@tool
def write_file(filename: str, content: str) -> str:
    """
    Writes code or documentation to a file. 
    Use this to create .md, .yaml, .sql, .py, or .tf files.
    """
    path = os.path.join(WORKING_DIRECTORY, filename)
    try:
        # Ensure parent dirs exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filename}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def read_file(filename: str) -> str:
    """Reads the content of a file."""
    path = os.path.join(WORKING_DIRECTORY, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

# LIST OF TOOLS TO EXPORT
architect_tools = [list_files, create_directory, write_file, read_file]