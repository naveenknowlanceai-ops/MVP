from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from app.agents.architect_agent.state import AgentState
from app.services.rag_service import rag_service

# --- IMPORT TOOLS ---
from app.agents.tools.filesystem import architect_tools
from app.agents.tools.atlassian_tools import atlassian_tools

# Combine all capabilities
ALL_TOOLS = architect_tools + atlassian_tools

# --- MODEL SETUP ---
# We bind the tools to the LLM so it knows it can use them
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.2, # Low temp for precise tool usage
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION,
    max_output_tokens=8192,
)

llm_with_tools = llm.bind_tools(ALL_TOOLS)

# --- NODES ---

def retrieve_node(state: AgentState):
    """Retrieves INTERNAL context from ChromaDB (The 'Bible')."""
    print(f"[ARCHITECT] 🧠 Retrieving Internal Patterns for: {state['request']}")
    try:
        docs = rag_service.search(state['request'])
        context = "\n\n".join([d.page_content for d in docs])
    except:
        context = "Standard Architectural Patterns apply."
    return {"rag_context": context, "revision_count": 0}

def reasoner_node(state: AgentState):
    """
    The Master Node.
    It looks at the Request + RAG + History and decides:
    1. Should I write a file?
    2. Should I check Jira?
    3. Should I publish to Confluence?
    4. Am I done?
    """
    print(f"[ARCHITECT] 🤔 Strategic Reasoning...")
    
    # 1. Construct the 'Mental Model' Prompt
    system_prompt = f"""
    ROLE: Principal Software Solution Architect (TOGAF/Agile).
    
    YOU ARE DEFINED BY THIS JOB DESCRIPTION:
    - You bridge Business Goals and Technical Execution.
    - You manage Risk (Security, Scalability, Cost).
    - You produce standardized Artifacts (ADD, ADR, API Specs).
    
    INTERNAL KNOWLEDGE (Your Brain):
    {state['rag_context']}
    
    YOUR TOOLKIT:
    1. FileSystem: Create directories, write 'architecture.md', 'api.yaml'.
    2. Jira: Check assigned tickets, create sub-tasks for Developers.
    3. Confluence: Publish your final designs.
    
    OPERATIONAL PROTOCOL:
    1. ANALYZE: If you haven't, check Jira for tickets assigned to you.
    2. DESIGN: Create the architecture artifacts (MD, Mermaid, YAML) in the workspace.
    3. DIAGRAM: Always include Mermaid.js diagrams in your Markdown.
    4. PUBLISH: Upload the finished design to Confluence.
    5. DELEGATE: Create Jira sub-tasks for the Developer Agent.
    
    CURRENT STATUS:
    User Request: "{state['request']}"
    """
    
    # 2. Build Message Chain
    # We pass the conversation history so the agent knows what tools it just ran
    # LangGraph passes 'messages' in the state if we used the standard MessageGraph,
    # but here we construct it manually for control.
    
    messages = [SystemMessage(content=system_prompt)] + state.get("message_history", [])
    
    # If this is the first turn, add the user request explicitly if not in history
    if not state.get("message_history"):
        messages.append(HumanMessage(content=state['request']))

    # 3. Invoke the Brain
    response = llm_with_tools.invoke(messages)
    
    # 4. Update Design Doc (If the LLM generated text along with tool calls)
    return {"design_doc": response}

def tool_execution_router(state: AgentState):
    """Decides if we loop back to Reasoner or End."""
    last_message = state['design_doc']
    
    # If the LLM made Tool Calls, go to the Tool Node
    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        return "tools"
    
    # If no tools called, we are done (or waiting for user)
    return END

# --- WORKFLOW ---
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reasoner", reasoner_node)
workflow.add_node("tools", ToolNode(ALL_TOOLS)) # LangGraph's prebuilt Tool Executor

# Edges
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "reasoner")

# Conditional: Reasoner -> Tools OR End
workflow.add_conditional_edges(
    "reasoner",
    tool_execution_router,
    {
        "tools": "tools",
        END: END
    }
)

# Cyclic: Tools -> Reasoner (The Agent sees the tool output and decides what to do next)
workflow.add_edge("tools", "reasoner")

architect_graph = workflow.compile()