from langchain_core.tools import tool
from app.services.jira_service import jira_service
from app.services.confluence_service import confluence_service

@tool
def check_jira_tickets() -> str:
    """Checks for Jira tickets assigned to the Architect."""
    return jira_service.get_assigned_tickets()

@tool
def create_developer_task(parent_ticket_id: str, summary: str, instructions: str) -> str:
    """Creates a sub-task in Jira for the Developer Agent. Useful for breaking down work."""
    return jira_service.create_subtask(parent_ticket_id, summary, instructions)

@tool
def publish_design_doc(title: str, content: str) -> str:
    """Publishes the High Level Design document to Confluence."""
    return confluence_service.create_page(title, content)

# Export for graph.py
atlassian_tools = [check_jira_tickets, create_developer_task, publish_design_doc]