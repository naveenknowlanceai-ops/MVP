import requests
import json
import markdown
from requests.auth import HTTPBasicAuth
from typing import Optional

class ConfluenceService:
    def __init__(self):
        self.base_url = None
        self.auth = None

    def configure(self, domain: str, email: str, api_token: str):
        """Sets up the connection (Reuses Jira Creds)."""
        domain = domain.strip().lower()
        if "://" in domain:
            domain = domain.split("://")[1]
        if "/" in domain:
            domain = domain.split("/")[0]
            
        # Confluence API v1 (Stable for Page Creation)
        self.base_url = f"https://{domain}/wiki/rest/api"
        self.auth = HTTPBasicAuth(email.strip(), api_token.strip())
        self.headers = {
            "Content-Type": "application/json"
        }

    def create_page(self, space_key: str, title: str, markdown_content: str) -> Optional[str]:
        if not self.base_url: return None

        # 1. Convert Markdown to HTML
        # Confluence uses 'Storage Format' which is basically HTML
        html_content = markdown.markdown(markdown_content)

        # 2. Prepare Payload
        payload = {
            "title": title,
            "type": "page",
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            }
        }

        try:
            # 3. Create Page
            url = f"{self.base_url}/content"
            print(f"[CONFLUENCE] Creating page '{title}' in space '{space_key}'...")
            
            response = requests.post(url, auth=self.auth, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                base = data['_links']['base']
                webui = data['_links']['webui']
                # Return the full clickable URL
                return f"{base}{webui}"
            else:
                print(f"[CONFLUENCE ERROR] {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"[CONFLUENCE EXCEPTION] {e}")
            return None

confluence_service = ConfluenceService()