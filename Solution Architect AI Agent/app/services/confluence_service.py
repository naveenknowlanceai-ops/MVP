import requests
import json
from requests.auth import HTTPBasicAuth
from typing import Tuple

class ConfluenceService:
    def __init__(self):
        self.base_url = None
        self.auth = None
        self.space_key = None

    def configure(self, domain: str, email: str, api_token: str, space_key: str):
        domain = domain.strip().lower()
        if "://" in domain: domain = domain.split("://")[1]
        if "/" in domain: domain = domain.split("/")[0]
            
        self.base_url = f"https://{domain}/wiki/rest/api"
        self.space_key = space_key.strip().upper()
        self.auth = HTTPBasicAuth(email.strip(), api_token.strip())
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_page(self, title: str, html_body: str) -> str:
        """Publishes a page to Confluence."""
        if not self.base_url: return "Confluence not connected."
        
        # Confluence uses 'Storage Format' (XHTML)
        # We wrap the content in a simple storage block
        storage_value = f"<p>{html_body}</p>" 
        
        payload = {
            "title": title,
            "type": "page",
            "space": {"key": self.space_key},
            "body": {
                "storage": {
                    "value": storage_value,
                    "representation": "storage"
                }
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/content", auth=self.auth, headers=self.headers, json=payload)
            if response.status_code == 200:
                link = response.json().get('_links', {}).get('base', '') + response.json().get('_links', {}).get('webui', '')
                return f"Published to Confluence: {link}"
            else:
                return f"Failed to publish: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error: {e}"

confluence_service = ConfluenceService()