from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.agents.qa_agent.graph import qa_graph

router = APIRouter()

class TestRequest(BaseModel):
    requirement: str
    previous_code: Optional[str] = ""
    feedback: Optional[str] = ""

class TestResponse(BaseModel):
    generated_code: str
    status: str
    logs: Optional[str] = "Simulation: Code Saved."

@router.post("/run", response_model=TestResponse)
async def run_qa_agent(request: TestRequest):
    try:
        initial_state = {
            "task": request.requirement,
            "generated_code": request.previous_code,
            "human_feedback": request.feedback,
            "rag_context": "",
            "revision_count": 0,
            "test_logs": "",
            "test_status": "INIT",
            "screenshot_path": ""
        }

        final_state = qa_graph.invoke(initial_state)
        
        return TestResponse(
            generated_code=final_state["generated_code"],
            status="SUCCESS",
            logs="Code generated and saved to sandbox."
        )

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))