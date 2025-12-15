import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings
from app.core.config import settings

DB_PATH = "./data/chroma_db"

class RAGService:
    def __init__(self):
        # Initialize Google Cloud Embeddings (No local GPU usage)
        self.embeddings = VertexAIEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            project=settings.GOOGLE_CLOUD_PROJECT
        )
        self.db = None

    def initialize_db(self):
        """Loads the ChromaDB from disk."""
        self.db = Chroma(
            persist_directory=DB_PATH, 
            embedding_function=self.embeddings
        )
        print(f"✅ RAG Service: Connected to Vector DB at {DB_PATH}")

    def ingest_knowledge(self, file_path: str):
        """
        One-time setup: Reads the PM Manual and stores it in the Brain.
        """
        print(f"📂 Loading knowledge from: {file_path}")
        
        # 1. Load Data
        loader = TextLoader(file_path)
        documents = loader.load()
        
        # 2. Split (PMs need context, so 1000 chars is a good balance)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        # 3. Create Vector Store (Uses Google Cloud for embeddings)
        # If DB exists, we add to it. If not, we create it.
        print("🧠 Generatings Embeddings via Vertex AI (Cloud)...")
        self.db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=DB_PATH
        )
        print(f"🎉 Success: Ingested {len(chunks)} knowledge chunks into PM Agent Brain.")

    def search(self, query: str, k: int = 4):
        """Retrieves relevant PM best practices."""
        if not self.db:
            self.initialize_db()
        return self.db.similarity_search(query, k=k)

# Singleton instance
rag_service = RAGService()