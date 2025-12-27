from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage
from app.agents.dev_agent.graph import dev_graph

router = APIRouter()

class DevRequest(BaseModel):
    task: str
    thread_id: str = "default_session" # Default if not provided

@router.post("/run")
async def run_developer(request: DevRequest):
    print(f"📥 REQUEST (Thread: {request.thread_id}): {request.task}")
    
    try:
        # Configuration tells LangGraph WHICH memory to load
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # We only pass the NEW message. 
        # The Graph automatically loads previous messages from SQLite.
        initial_state = {
            "messages": [HumanMessage(content=request.task)],
            "current_task": request.task,
            "last_status": "active"
        }
        
        # Invoke (The graph now merges old + new memory)
        print("🧠 Waking up Agent...")
        final_state = dev_graph.invoke(initial_state, config=config)
        
        # Extract response
        last_msg = final_state["messages"][-1]
        response_text = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        
        return {
            "status": "success",
            "response": response_text
        }

    except Exception as e:
        print(f"❌ MEMORY ERROR: {e}")
        return {
            "status": "error",
            "response": f"System Error: {str(e)}"
        }