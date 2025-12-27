from typing import TypedDict

class AgentState(TypedDict):
    """
    Memory structure for the QA Agent.
    """
    task: str                 # The test requirement
    rag_context: str          # Knowledge from DB
    
    generated_code: str       # The Python Playwright script
    test_logs: str           # Output from the test run
    test_status: str          # "PASS", "FAIL", "ERROR"
    screenshot_path: str      # Path to failure screenshot
    
    human_feedback: str       # Correction from user
    revision_count: int