from typing import TypedDict

class AgentState(TypedDict):
    """
    Memory structure for the Solution Architect.
    """
    request: str              # User's request
    rag_context: str          # Retrieved patterns
    design_doc: str           # The HLD / Markdown output
    human_feedback: str       # User corrections
    revision_count: int