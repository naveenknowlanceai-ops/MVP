from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.agents.qa_agent.state import AgentState
from app.services.rag_service import rag_service
import os

# --- 1. MODEL SETUP ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.0,  # Zero temp for precise coding
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION
)

# --- 2. NODES ---

def retrieve_node(state: AgentState):
    """Retrieves standard testing patterns"""
    print(f"[QA AGENT] Checking KB for: {state['task']}")
    try:
        docs = rag_service.search(state['task'])
        context = "\n\n".join([d.page_content for d in docs])
    except:
        context = "Use standard Playwright best practices."
    return {"rag_context": context}

def engineer_node(state: AgentState):
    """Writes the Playwright Test Script"""
    print("[QA AGENT] Writing Automation Script...")
    
    prompt = f"""
    [ROLE]
    You are a Senior Test Automation Engineer using Python and Playwright.

    [CONTEXT]
    {state['rag_context']}

    [TASK]
    Write a complete Python Playwright script for: {state['task']}

    [RULES]
    1. Use 'sync_playwright'.
    2. Define a function 'run_test()'.
    3. Take screenshots on failure to 'sandbox/screenshots/error.png'.
    4. Print "TEST_PASSED" or "TEST_FAILED" clearly.
    5. Output ONLY the Python Code. No markdown backticks.

    [USER FEEDBACK/ERROR]
    {state.get('human_feedback', '')}
    {state.get('test_logs', '')}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Cleanup markdown if LLM adds it
    clean_code = response.content.replace("```python", "").replace("```", "").strip()
    
    return {
        "generated_code": clean_code,
        "human_feedback": "" 
    }

def save_code_node(state: AgentState):
    """Saves the code to the sandbox (Mock execution for now)"""
    file_path = f"{settings.SANDBOX_PATH}/code/current_test.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(state['generated_code'])
    
    return {"test_status": "READY_TO_RUN"}

# --- 3. WORKFLOW ---

workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("engineer", engineer_node)
workflow.add_node("save_code", save_code_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "engineer")
workflow.add_edge("engineer", "save_code")
workflow.add_edge("save_code", END)

qa_graph = workflow.compile()