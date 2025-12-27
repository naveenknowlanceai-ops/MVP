from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    current_task: str
    rag_context: str
    prd_content: str
    human_feedback: str
    revision_count: int
    # --- NEW: Store Structured Tickets ---
    generated_tickets: Optional[List[dict]]