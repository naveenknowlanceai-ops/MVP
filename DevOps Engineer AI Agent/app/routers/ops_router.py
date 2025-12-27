from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.agents.devops_agent.graph import devops_graph

router = APIRouter()

class OpsRequest(BaseModel):
    command: str
    current_code: Optional[str] = ""
    intercept_msg: Optional[str] = ""

class OpsResponse(BaseModel):
    iac_output: str
    status: str

@router.post("/execute", response_model=OpsResponse)
async def execute_ops(request: OpsRequest):
    try:
        initial_state = {
            "mission": request.command,
            "terraform_plan": request.current_code,
            "human_approval": request.intercept_msg,
            "rag_context": "",
            "deployment_log": "",
            "iteration": 0
        }
        
        final_state = devops_graph.invoke(initial_state)
        
        return OpsResponse(
            iac_output=final_state["terraform_plan"],
            status="success"
        )
    except Exception as e:
        print(f"[ERROR] Ops Core: {e}")
        raise HTTPException(status_code=500, detail=str(e))