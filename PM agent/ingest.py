import os
import sys

# 1. LOAD ENVIRONMENT FIRST
from dotenv import load_dotenv
load_dotenv()

# 2. Fix Encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 3. Import Service
from app.services.rag_service import rag_service

def main():
    # Make sure this file exists in your folder!
    file_path = "pm_role_clarity.md"
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Could not find {file_path}")
        return

    print("--- STARTING BRAIN INGESTION ---")
    rag_service.ingest_knowledge(file_path)
    print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()