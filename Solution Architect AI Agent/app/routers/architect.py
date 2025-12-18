from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.agents.architect_agent.graph import architect_graph

router = APIRouter()

class ArchitectRequest(BaseModel):
    request: str
    current_design: Optional[str] = ""
    feedback: Optional[str] = ""

class ArchitectResponse(BaseModel):
    design_doc: str
    status: str

@router.post("/design", response_model=ArchitectResponse)
async def run_architect(request: ArchitectRequest):
    try:
        initial_state = {
            "request": request.request,
            "design_doc": request.current_design,
            "human_feedback": request.feedback,
            "rag_context": "",
            "revision_count": 0
        }

        # Run the graph
        final_state = architect_graph.invoke(initial_state)

        return ArchitectResponse(
            design_doc=final_state["design_doc"],
            status="success"
        )

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))