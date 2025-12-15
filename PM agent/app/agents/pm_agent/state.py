from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    """
    The Memory of the PM Agent.
    This dict is passed between every node in the graph.
    """
    # The conversation so far
    messages: List[str] 
    
    # The user's specific request (e.g., "Create a feature for login")
    current_task: str
    
    # The 'Live' Artifact - The PRD being built
    prd_content: str
    
    # Feedback provided by the human during the 'Interrupt' phase
    human_feedback: str
    
    # Internal reasoning logs (what the agent found in RAG)
    rag_context: str
    
    # Status flags
    revision_count: int
    is_finished: bool