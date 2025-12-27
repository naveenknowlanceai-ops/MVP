import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Encoding Fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.rag_service import rag_service

def main():
    # You will create this file later to teach the agent about your specific infrastructure rules
    file_path = "system_instructions.md"
    
    # Create dummy file if not exists to prevent crash
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Google Cloud Best Practices\nUse VPCs for all deployments.\nAlways enable shielding on GKE nodes.")

    print("--- STARTING DEVOPS KNOWLEDGE INGESTION ---")
    rag_service.ingest_knowledge(file_path)
    print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()