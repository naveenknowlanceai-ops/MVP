import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = VertexAIEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        self.db = None
        self.persist_path = settings.CHROMA_PERSIST_DIRECTORY

    def initialize_db(self):
        self.db = Chroma(
            persist_directory=self.persist_path,
            embedding_function=self.embeddings
        )
        print(f"[INFO] QA Knowledge Base Connected.")

    def ingest_knowledge(self, file_path: str):
        print(f"[INFO] Loading: {file_path}")
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            
            self.db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_path
            )
            print(f"[SUCCESS] Ingested {len(chunks)} chunks.")
        except Exception as e:
            print(f"[ERROR] Ingestion Failed: {e}")

    def search(self, query: str, k: int = 4):
        if not self.db:
            self.initialize_db()
        return self.db.similarity_search(query, k=k)

rag_service = RAGService()