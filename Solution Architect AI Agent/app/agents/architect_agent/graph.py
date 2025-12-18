from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.agents.architect_agent.state import AgentState
from app.services.rag_service import rag_service

# --- 1. MODEL SETUP ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.2, # Lower temperature for technical precision
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION
)

# --- 2. NODES ---

def retrieve_node(state: AgentState):
    """Retrieves architectural patterns"""
    print(f"[ARCHITECT] Searching patterns for: {state['request']}")
    try:
        docs = rag_service.search(state['request'])
        context = "\n\n".join([d.page_content for d in docs])
    except:
        context = "No specific patterns found in knowledge base."
    return {"rag_context": context}

def draft_node(state: AgentState):
    """Generates the High-Level Design (HLD)"""
    print("[ARCHITECT] Designing solution...")
    
    prompt = f"""
    [ROLE]
    You are a Principal Solution Architect.
    
    [CONTEXT FROM KNOWLEDGE BASE]
    {state['rag_context']}
    
    [INSTRUCTIONS]
    1. Create a High-Level Design (HLD) Document in Markdown.
    2. Define the Tech Stack (Frontend, Backend, DB, Cloud) with reasoning.
    3. Include a Mermaid.js diagram block (```mermaid ... ```) depicting the architecture.
    4. List 3 key technical risks.
    
    [USER REQUEST]
    {state['request']}
    """
    
    if state.get("human_feedback"):
        prompt += f"""
        
        [FEEDBACK INSTRUCTION]
        The user wants changes. Update the design below:
        
        FEEDBACK: {state['human_feedback']}
        
        CURRENT DESIGN:
        {state.get('design_doc')}
        """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "design_doc": response.content,
        "human_feedback": "" 
    }

# --- 3. WORKFLOW ---
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("draft", draft_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "draft")
workflow.add_edge("draft", END)

architect_graph = workflow.compile()