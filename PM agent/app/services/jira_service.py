import requests
import json
from requests.auth import HTTPBasicAuth
from typing import Optional, Tuple

class JiraService:
    def __init__(self):
        self.base_url = None
        self.auth = None
        self.project_key = None

    def configure(self, domain: str, email: str, api_token: str, project_key: str):
        """Sets up the connection."""
        domain = domain.strip().lower()
        if "://" in domain:
            domain = domain.split("://")[1]
        if "/" in domain:
            domain = domain.split("/")[0]
            
        self.base_url = f"https://{domain}/rest/api/3"
        self.project_key = project_key.strip().upper()
        self.auth = HTTPBasicAuth(email.strip(), api_token.strip())
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
            
            if response.status_code == 401:
                return False, "Auth Failed. Check Email & Token."
            if response.status_code != 200:
                return False, f"Connection Error: {response.status_code}"

            # Check Project
            url = f"{self.base_url}/project/{self.project_key}"
            response = requests.get(url, auth=self.auth, headers=self.headers, timeout=10)
            if response.status_code == 404:
                return False, f"Project '{self.project_key}' not found."
            
            return True, "Connected!"
        except Exception as e:
            return False, f"Network Error: {e}"

    def create_issue(self, summary: str, description: str, issuetype: str = "Story") -> Optional[str]:
        if not self.base_url: return None

        # 1. Prepare Description (Atlassian Format)
        description_adf = {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": description}]
            }]
        }

        # 2. Define Helper to send request
        def send_request(type_name):
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description_adf,
                    "issuetype": {"name": type_name}
                }
            }
            return requests.post(f"{self.base_url}/issue", auth=self.auth, headers=self.headers, json=payload)

        # 3. Attempt 1: Try requested type (usually "Story")
        print(f"[JIRA] Attempting create with type: {issuetype}")
        response = send_request(issuetype)

        # 4. Attempt 2: Auto-Fallback to "Task" if "Story" is invalid
        if response.status_code == 400 and "issuetype" in response.text:
            print(f"[JIRA] '{issuetype}' not supported. Retrying as 'Task'...")
            response = send_request("Task")

        # 5. Handle Result
        if response.status_code == 201:
            data = response.json()
            key = data['key']
            domain = self.base_url.split("/rest")[0]
            return f"{domain}/browse/{key}"
        else:
            print(f"[JIRA ERROR] {response.status_code}: {response.text}")
            return None

jira_service = JiraService()