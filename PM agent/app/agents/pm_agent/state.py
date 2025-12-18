from typing import TypedDict

class AgentState(TypedDict):
    """
    Memory structure for the Agent.
    """
    current_task: str
    rag_context: str
    prd_content: str
    human_feedback: str
    revision_count: int