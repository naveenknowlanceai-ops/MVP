import vertexai
from app.core.config import settings

def init_vertex_ai():
    """Initializes the connection to Google Cloud Vertex AI"""
    try:
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT, 
            location=settings.LOCATION
        )
        print(f"✅ Connected to Vertex AI Project: {settings.GOOGLE_CLOUD_PROJECT}")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Vertex AI: {e}")
        return False