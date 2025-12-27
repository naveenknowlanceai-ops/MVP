from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.jira_service import jira_service
from app.services.confluence_service import confluence_service

router = APIRouter()

class JiraConfig(BaseModel):
    domain: str
    email: str
    token: str
    project_key: str

class ConfluenceConfig(BaseModel):
    domain: str
    email: str
    token: str
    space_key: str

@router.post("/jira/connect")
async def connect_jira(config: JiraConfig):
    jira_service.configure(config.domain, config.email, config.token, config.project_key)
    success, msg = jira_service.test_connection()
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "connected", "message": msg}

@router.post("/confluence/connect")
async def connect_confluence(config: ConfluenceConfig):
    confluence_service.configure(config.domain, config.email, config.token, config.space_key)
    # Simple test for Confluence (optional)
    return {"status": "connected", "message": "Confluence Configured"}