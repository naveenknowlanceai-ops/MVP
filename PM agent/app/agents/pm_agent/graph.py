from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.agents.pm_agent.state import AgentState
from app.services.rag_service import rag_service

# --- 1. IMPORT GOOGLE PROTOBUF TYPES ---
# We need the raw objects to bypass LangChain's dictionary validation
try:
    from google.cloud.aiplatform_v1beta1.types import Tool, GoogleSearchRetrieval
except ImportError:
    # Fallback for older environments, though your reqs should have this
    from google.cloud.aiplatform_v1.types import Tool, GoogleSearchRetrieval

# --- 2. MODEL SETUP ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.3,
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION,
    max_output_tokens=8192,
)

# --- 3. NODES ---

def retrieve_node(state: AgentState):
    """Retrieves INTERNAL context"""
    print(f"[AGENT] 🧠 Checking Internal Knowledge for: {state['current_task']}")
    try:
        docs = rag_service.search(state['current_task'])
        context = "\n\n".join([d.page_content for d in docs])
    except:
        context = "No specific internal guidelines found."
    return {"rag_context": context}

def draft_node(state: AgentState):
    """Generates the PRD using Internal Knowledge + Google Search"""
    print("[AGENT] 🌍 Researching & Drafting (using Google Grounding)...")
    
    # --- CRITICAL FIX: CREATE PROTOBUF OBJECT ---
    # Instead of a dict, we create the actual Google Tool object.
    # This prevents the "REQUIRED_FIELD_MISSING" error.
    
    try:
        # We try to use the 'google_search_retrieval' field (Standard)
        # If the API complains again about "use google_search", we will catch it.
        tool_config = Tool(
            google_search_retrieval=GoogleSearchRetrieval()
        )
    except Exception:
        # Fallback if the SDK is very new and expects different kwargs
        tool_config = None
        print("[WARNING] Could not construct Google Search Tool object.")

    prompt = f"""
    [ROLE]
    You are an Expert Product Manager.
    
    [INTERNAL KNOWLEDGE]
    {state['rag_context']}
    
    [TASK]
    {state['current_task']}
    
    [INSTRUCTIONS]
    1. Write a detailed Product Requirements Document (PRD).
    2. USE GOOGLE SEARCH to find current competitors, market trends, or technical standards.
    3. INTEGRATE the search findings into the content.
    4. Output strictly Markdown.
    """
    
    if state.get("human_feedback"):
        prompt += f"""
        [FEEDBACK]
        Refine based on: {state['human_feedback']}
        
        [PREVIOUS DRAFT]
        {state.get('prd_content')}
        """
    
    try:
        # Bind the PROTOBUF object, not a dict
        if tool_config:
            llm_with_search = llm.bind(tools=[tool_config])
            response = llm_with_search.invoke([HumanMessage(content=prompt)])
        else:
            response = llm.invoke([HumanMessage(content=prompt)])
            
        content = response.content
        
    except Exception as e:
        print(f"[WARNING] Grounding failed: {e}. Falling back to standard generation.")
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content

    return {
        "prd_content": content,
        "human_feedback": "" 
    }

# --- 4. WORKFLOW ---
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("draft", draft_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "draft")
workflow.add_edge("draft", END)

pm_graph = workflow.compile()