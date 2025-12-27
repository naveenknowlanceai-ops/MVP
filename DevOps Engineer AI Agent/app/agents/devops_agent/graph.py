from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.agents.devops_agent.state import DevOpsState
from app.services.rag_service import rag_service

# --- 1. MODEL SETUP ---
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.1, # Low temp for precise Code Generation
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION
)

# --- 2. NODES ---

def retrieve_infrastructure_context(state: DevOpsState):
    """Check documentation or past deployments"""
    print(f"[AGENT] Analysing infrastructure requirements for: {state['mission']}")
    try:
        docs = rag_service.search(state['mission'])
        context = "\n\n".join([d.page_content for d in docs])
    except:
        context = "Standard GCP/Terraform Standards apply."
    return {"rag_context": context}

def engineer_solution(state: DevOpsState):
    """Generates the Terraform Code"""
    print("[AGENT] Architecting Solution...")
    
    prompt = f"""
    [ROLE]
    You are a Senior Principal Cloud Engineer.

    [CONTEXT]
    {state['rag_context']}

    [INSTRUCTIONS]
    Write the Terraform (HCL) code required to solve the task.
    Do not explain. Return ONLY valid HCL code inside a markdown block.
    Include comments for security/best practices.

    [TASK]
    {state['mission']}
    
    [FEEDBACK/INTERCEPT]
    {state.get('human_approval', '')}
    
    [PREVIOUS PLAN]
    {state.get('terraform_plan', '')}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "terraform_plan": response.content,
        "human_approval": "" # Reset trigger
    }

# --- 3. WORKFLOW ---
workflow = StateGraph(DevOpsState)

workflow.add_node("retrieve", retrieve_infrastructure_context)
workflow.add_node("engineer", engineer_solution)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "engineer")
workflow.add_edge("engineer", END)

devops_graph = workflow.compile()