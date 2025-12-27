from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from app.agents.architect_agent.graph import architect_graph

router = APIRouter()

class ArchitectRequest(BaseModel):
    request: str
    current_design: Optional[str] = ""
    message_history: List[str] = []

class ArchitectResponse(BaseModel):
    design_doc: str
    message_history: List[str]
    status: str
    approval_state: str = "PENDING"

@router.post("/design", response_model=ArchitectResponse)
async def run_architect(request: ArchitectRequest):
    try:
        initial_state = {
            "request": request.request,
            "design_doc": request.current_design,
            "message_history": request.message_history,
            "rag_context": "",
            "critique_comments": "",
            "approval_status": "PENDING",
            "revision_count": 0
        }

        # Run the graph
        final_state = await architect_graph.ainvoke(initial_state)

        # --- BUG FIX: EXTRACT TEXT FROM AI MESSAGE ---
        # The graph returns an AIMessage object (with .content and .tool_calls)
        # We need to extract just the string content for the Frontend.
        
        raw_output = final_state.get("design_doc", "")
        final_doc_text = ""
        
        if hasattr(raw_output, 'content'):
            final_doc_text = raw_output.content
        elif isinstance(raw_output, str):
            final_doc_text = raw_output
        else:
            final_doc_text = str(raw_output)

        # Append interaction to history
        new_history = request.message_history
        new_history.append(f"User: {request.request}")
        new_history.append(f"Architect: [Response Generated]")

        return ArchitectResponse(
            design_doc=final_doc_text,
            message_history=new_history,
            status="success",
            approval_state=final_state.get("approval_status", "PENDING")
        )

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        # Print full stack trace in terminal for debugging if needed
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))