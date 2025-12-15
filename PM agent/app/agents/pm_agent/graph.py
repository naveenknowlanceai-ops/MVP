import operator
from typing import Annotated, Any, Dict
from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config import settings
from app.agents.pm_agent.state import AgentState
from app.services.rag_service import rag_service

# --- 1. SETUP MODEL ---
# We use the Cloud Model defined in config (Gemini 1.5 Pro)
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.3, # Low temperature for professional, consistent output
    max_output_tokens=8192,
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION
)

# --- 2. DEFINE NODES ---

def retrieve_knowledge_node(state: AgentState):
    """
    Step 1: Consult the 'Bible' (Your uploaded markdown).
    This ensures the agent acts like *YOU* want, not just a generic AI.
    """
    print(f"--- 🧠 RECALLING: {state['current_task']} ---")
    
    # Search the vector DB for relevant PM practices
    query = state['current_task']
    docs = rag_service.search(query, k=3)
    
    # Collapse docs into a single string
    context_str = "\n\n".join([d.page_content for d in docs])
    
    return {"rag_context": context_str}

def drafter_node(state: AgentState):
    """
    Step 2: The Core Writing Engine.
    Generates the PRD based on User Input + RAG Context + Previous Feedback.
    """
    print("--- ✍️ DRAFTING CONTENT ---")
    
    task = state['current_task']
    context = state['rag_context']
    current_doc = state.get('prd_content', "")
    feedback = state.get('human_feedback', "")
    
    # Dynamic Prompt Construction
    system_prompt = f"""
    You are an Expert Product Manager Agent.
    
    YOUR KNOWLEDGE BASE (Best Practices):
    {context}
    
    INSTRUCTIONS:
    1. You are drafting a Product Requirements Document (PRD).
    2. Output strictly in MARKDOWN format.
    3. Be professional, concise, and metric-driven.
    4. If there is existing content, you are UPDATING it based on feedback.
    """
    
    if feedback:
        user_message = f"""
        UPDATE this PRD based on my feedback.
        
        CURRENT DRAFT:
        {current_doc}
        
        MY FEEDBACK:
        {feedback}
        
        Only output the updated Markdown.
        """
    else:
        user_message = f"""
        Draft a new PRD for this request: "{task}"
        
        Include:
        - Problem Statement
        - Target Audience
        - User Stories
        - Success Metrics (KPIs)
        """

    # Invoke Gemini
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]
    
    response = llm.invoke(messages)
    
    return {
        "prd_content": response.content,
        "revision_count": state.get("revision_count", 0) + 1,
        "human_feedback": "" # Clear feedback after handling it
    }

# --- 3. BUILD THE GRAPH ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("retrieve", retrieve_knowledge_node)
workflow.add_node("draft", drafter_node)

# Add Edges
# Flow: Start -> Retrieve Knowledge -> Draft -> End (Wait for Human)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "draft")
workflow.add_edge("draft", END)

# Compile
# We don't use MemorySaver here yet because the State is managed by the API/Frontend
pm_graph = workflow.compile()