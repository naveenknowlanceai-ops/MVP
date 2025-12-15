import os
from app.services.rag_service import rag_service

# Ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

def main():
    file_path = "pm_role_clarity.md"
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find {file_path}. Please create it.")
        return

    print("--- STARTING BRAIN INGESTION ---")
    rag_service.ingest_knowledge(file_path)
    print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()