import requests
import json
from requests.auth import HTTPBasicAuth
from typing import Optional, Tuple, List, Dict

class JiraService:
    def __init__(self):
        self.base_url = None
        self.auth = None
        self.project_key = None
        self.email = None # Needed to identify "currentUser"

    def configure(self, domain: str, email: str, api_token: str, project_key: str):
        """Sets up the connection at Runtime."""
        domain = domain.strip().lower()
        if "://" in domain:
            domain = domain.split("://")[1]
        if "/" in domain:
            domain = domain.split("/")[0]
            
        self.base_url = f"https://{domain}/rest/api/3"
        self.project_key = project_key.strip().upper()
        self.email = email.strip()
        self.auth = HTTPBasicAuth(self.email, api_token.strip())
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def test_connection(self) -> Tuple[bool, str]:
        if not self.base_url: return False, "Not Configured"
        try:
            # Check User
            url = f"{self.base_url}/myself"
            response = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
            if response.status_code != 200: return False, "Auth Failed"
            
            # Check Project
            url = f"{self.base_url}/project/{self.project_key}"
            response = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
            if response.status_code == 404: return False, "Project Not Found"
            
            return True, "Connected"
        except Exception as e:
            return False, str(e)

    def get_assigned_tickets(self) -> str:
        """Fetches tickets assigned to the logged-in user."""
        if not self.base_url: return "Jira not connected."
        
        # JQL: assigned to me AND not done
        jql = f"assignee = '{self.email}' AND statusCategory != Done ORDER BY created DESC"
        
        url = f"{self.base_url}/search"
        params = {"jql": jql, "fields": "summary,description,status,priority", "maxResults": 5}
        
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            if response.status_code != 200: return f"Error fetching tickets: {response.text}"
            
            issues = response.json().get("issues", [])
            if not issues: return "No active tickets assigned to you."
            
            result = []
            for issue in issues:
                key = issue['key']
                summary = issue['fields']['summary']
                # Extract plain text from description (simplified)
                desc = "No description" 
                if issue['fields'].get('description'):
                    # Very basic handling of ADF, usually the agent just needs the summary
                    desc = "(Description content available)" 
                
                result.append(f"[{key}] {summary}")
            
            return "\n".join(result)
        except Exception as e:
            return f"Network Error: {e}"

    def create_subtask(self, parent_key: str, summary: str, description: str) -> str:
        """Creates a Sub-task for Developers."""
        if not self.base_url: return "Jira not connected."
        
        # Simple ADF wrapper
        description_adf = {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
        }

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "parent": {"key": parent_key},
                "summary": summary,
                "description": description_adf,
                "issuetype": {"name": "Sub-task"}
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/issue", auth=self.auth, headers=self.headers, json=payload)
            if response.status_code == 201:
                return f"Created Sub-task: {response.json()['key']}"
            else:
                return f"Failed to create subtask: {response.text}"
        except Exception as e:
            return f"Error: {e}"

jira_service = JiraService()