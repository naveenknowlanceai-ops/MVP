import os
import sys
from dotenv import load_dotenv

load_dotenv()

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from app.services.rag_service import rag_service

def main():
    file_path = "architect_patterns.md"
    
    if not os.path.exists(file_path):
        # Create a dummy file if it doesn't exist so it works immediately
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Architecture Patterns\nUse Microservices for high scalability.\nUse Monolith for MVP speed.")
        print("[INFO] Created dummy architect_patterns.md")

    print("--- STARTING ARCHITECT BRAIN INGESTION ---")
    rag_service.ingest_knowledge(file_path)
    print("--- INGESTION COMPLETE ---")

if __name__ == "__main__":
    main()