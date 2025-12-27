from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Memory structure for the Solution Architect.
    """
    request: str                  # The latest user prompt
    rag_context: str              # Internal knowledge (Patterns)
    design_doc: str               # The evolving Markdown document
    message_history: List[str]    # <-- NEW: Chat log for context
    revision_count: int