from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import the graph we just built
from app.agents.pm_agent.graph import pm_graph

router = APIRouter()

# --- Request/Response Schemas ---
class AgentRequest(BaseModel):
    task: str
    current_prd: Optional[str] = ""
    feedback: Optional[str] = ""

class AgentResponse(BaseModel):
    prd_content: str
    status: str

# --- The Endpoint ---
@router.post("/run", response_model=AgentResponse)
async def run_pm_agent(request: AgentRequest):
    """
    This endpoint triggers the Agentic Workflow.
    It handles both "New Tasks" and "Refinements" (Coworking).
    """
    try:
        # 1. Prepare Initial State
        initial_state = {
            "current_task": request.task,
            "prd_content": request.current_prd,
            "human_feedback": request.feedback,
            "messages": [],
            "rag_context": "",
            "revision_count": 0,
            "is_finished": False
        }

        # 2. Run the Graph
        # We use .invoke() to run the full chain (Retrieve -> Draft)
        final_state = pm_graph.invoke(initial_state)

        # 3. Return result to Frontend
        return AgentResponse(
            prd_content=final_state["prd_content"],
            status="success"
        )

    except Exception as e:
        print(f"❌ Error running Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))