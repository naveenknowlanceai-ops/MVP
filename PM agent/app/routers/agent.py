from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.agents.pm_agent.graph import pm_graph

router = APIRouter()

class AgentRequest(BaseModel):
    task: str
    current_prd: Optional[str] = ""
    feedback: Optional[str] = ""

class AgentResponse(BaseModel):
    prd_content: str
    status: str

@router.post("/run", response_model=AgentResponse)
async def run_pm_agent(request: AgentRequest):
    try:
        initial_state = {
            "current_task": request.task,
            "prd_content": request.current_prd,
            "human_feedback": request.feedback,
            "rag_context": "",
            "revision_count": 0
        }

        # Run the graph
        final_state = pm_graph.invoke(initial_state)

        return AgentResponse(
            prd_content=final_state["prd_content"],
            status="success"
        )

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))