from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

# LangChain Imports
from langchain_core.messages import HumanMessage

# Application Imports
from app.agents.pm_agent.graph import pm_graph, llm
from app.services.db_service import db_service
from app.services.jira_service import jira_service
from app.services.confluence_service import confluence_service
router = APIRouter()

# --- DATA MODELS ---
class PublishRequest(BaseModel):
    space_key: str
    title: str
    content: str
class AgentRequest(BaseModel):
    thread_id: str
    task: str
    current_prd: Optional[str] = ""
    mode: str = "draft"  # Options: 'draft', 'tickets'

class AgentResponse(BaseModel):
    prd_content: str
    tickets: List[Dict[str, Any]] = []
    status: str

class JiraConfig(BaseModel):
    domain: str
    email: str
    token: str
    project_key: str

class PushTicketRequest(BaseModel):
    summary: str
    description: str
    type: str

# --- JIRA INTEGRATION ENDPOINTS ---
@router.post("/integrations/confluence/publish")
async def publish_page(req: PublishRequest):
    """Publishes the current PRD to Confluence."""
    
    # 1. Load Creds (Reuse Jira Creds)
    domain = await db_service.get_setting("jira_domain")
    email = await db_service.get_setting("jira_email")
    token = await db_service.get_setting("jira_token")

    if not all([domain, email, token]):
        raise HTTPException(status_code=400, detail="Please connect Jira/Atlassian first.")

    # 2. Configure & Publish
    confluence_service.configure(domain, email, token)
    
    url = confluence_service.create_page(req.space_key, req.title, req.content)
    
    if url:
        return {"success": True, "url": url}
    else:
        # If it fails (e.g., page title already exists), we return false
        return {"success": False, "url": None}
        
@router.get("/integrations/jira/status")
async def get_jira_status():
    """
    Checks if Jira credentials exist in the database.
    Used by Frontend to show 'Connected' status on load.
    """
    domain = await db_service.get_setting("jira_domain")
    email = await db_service.get_setting("jira_email")
    project = await db_service.get_setting("jira_project")
    
    if domain and email and project:
        return {
            "is_connected": True, 
            "email": email, 
            "domain": domain,
            "project": project
        }
    return {"is_connected": False}

@router.post("/integrations/jira/connect")
async def connect_jira(config: JiraConfig):
    """
    Tests connection to Jira and saves credentials to SQLite if successful.
    """
    # 1. Configure the Service
    jira_service.configure(config.domain, config.email, config.token, config.project_key)
    
    # 2. Test Connection (Returns Tuple: Success, Message)
    success, message = jira_service.test_connection()
    
    if success:
        # 3. Save to Vault (DB) if valid
        await db_service.save_setting("jira_domain", config.domain)
        await db_service.save_setting("jira_email", config.email)
        await db_service.save_setting("jira_token", config.token)
        await db_service.save_setting("jira_project", config.project_key)
        return {"status": "connected", "message": message}
    else:
        # 4. Return Error to UI
        raise HTTPException(status_code=400, detail=message)

@router.post("/integrations/jira/push")
async def push_ticket(ticket: PushTicketRequest):
    """
    Pushes a single ticket to the connected Jira Project.
    """
    # 1. Load Credentials from DB
    domain = await db_service.get_setting("jira_domain")
    email = await db_service.get_setting("jira_email")
    token = await db_service.get_setting("jira_token")
    project = await db_service.get_setting("jira_project")

    if not all([domain, email, token, project]):
        raise HTTPException(status_code=400, detail="Jira not configured. Please connect first.")

    # 2. Re-configure Service
    jira_service.configure(domain, email, token, project)

    # 3. Create Issue
    url = jira_service.create_issue(ticket.summary, ticket.description, ticket.type)
    
    if url:
        return {"success": True, "ticket_url": url}
    else:
        return {"success": False, "ticket_url": None}

# --- MAIN AGENT ENDPOINT ---

@router.post("/run", response_model=AgentResponse)
async def run_pm_agent(request: AgentRequest):
    """
    The Brain of the operation. Handles two modes:
    1. 'draft': Runs the RAG -> Search -> Writer Graph.
    2. 'tickets': Runs the Scrum Master Logic to generate JSON.
    """
    try:
        # === MODE 1: SCRUM MASTER (Generate Tickets) ===
        if request.mode == "tickets":
            await db_service.add_message(request.thread_id, "user", "Generate Tickets")
            
            prompt = f"""
            [ROLE]
            You are a Technical Scrum Master.
            
            [INPUT PRD CONTENT]
            {request.current_prd}
            
            [TASK]
            Break this PRD into 5-8 granular Jira User Stories.
            
            [OUTPUT FORMAT]
            Strictly return a JSON Array. Do not use Markdown formatting like ```json.
            Example:
            [
                {{"summary": "Implement Login API", "description": "Create POST /login endpoint...", "points": 3, "type": "Story"}},
                {{"summary": "Design Login UI", "description": "Create React components...", "points": 2, "type": "Story"}}
            ]
            """
            
            # Direct LLM Call (Bypassing Graph for simplicity)
            response = llm.invoke([HumanMessage(content=prompt)])
            
            # Clean Logic
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            
            try:
                tickets = json.loads(clean_json)
            except json.JSONDecodeError:
                # Fallback if LLM returns bad JSON
                tickets = [{
                    "summary": "Error parsing tickets",
                    "description": "The Agent returned invalid JSON. Please try again.",
                    "points": 0,
                    "type": "Bug"
                }]

            await db_service.add_message(request.thread_id, "agent", f"Generated {len(tickets)} tickets.")
            
            return AgentResponse(
                prd_content=request.current_prd,
                tickets=tickets,
                status="success"
            )

        # === MODE 2: PM DRAFTER (Write PRD) ===
        else:
            # 1. Log User Input
            await db_service.add_message(request.thread_id, "user", request.task)
            
            # 2. Get Chat History
            history = await db_service.get_history(request.thread_id)
            history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history])

            # 3. Prepare Graph State
            initial_state = {
                "current_task": request.task,
                "prd_content": request.current_prd,
                "human_feedback": history_text,
                "rag_context": "",
                "revision_count": 0,
                "generated_tickets": []
            }

            # 4. Run LangGraph (RAG + Google Search + Write)
            final_state = pm_graph.invoke(initial_state)
            new_prd = final_state["prd_content"]

            # 5. Log & Save Result
            await db_service.add_message(request.thread_id, "agent", "Updated PRD.")
            await db_service.create_or_update_project(request.thread_id, new_prd)

            return AgentResponse(
                prd_content=new_prd,
                tickets=[],
                status="success"
            )

    except Exception as e:
        print(f"[ERROR] API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))