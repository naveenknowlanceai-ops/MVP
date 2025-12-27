import os
import sys
from dotenv import load_dotenv
load_dotenv()

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.rag_service import rag_service

def main():
    # You will create this file later with QA guidelines
    file_path = "system_instructions.md" 
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Could not find {file_path}. Create a dummy file to test.")
        # Create dummy file if missing to prevent error
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("QA Engineer Best Practices: Always use explicit waits in Playwright.")

    print("--- STARTING QA BRAIN INGESTION ---")
    rag_service.ingest_knowledge(file_path)
    print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()