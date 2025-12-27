from langgraph.graph import StateGraph, END
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, ToolMessage
from app.core.config import settings
from app.agents.dev_agent.state import DevAgentState
from app.agents.tools.filesystem import dev_tools
# Add run_shell_command import
from app.agents.tools.terminal import run_shell_command 
from app.agents.tools.filesystem import dev_tools as file_tools

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver # New Import

import os


# 1. MODEL SETUP (Bind Tools Immediately)
llm = ChatVertexAI(
    model_name=settings.MODEL_NAME,
    temperature=0.0, # Zero temp for coding precision
    project=settings.GOOGLE_CLOUD_PROJECT,
    location=settings.GOOGLE_CLOUD_LOCATION
)


all_tools = file_tools + [run_shell_command] 

llm_with_tools = llm.bind_tools(all_tools)
# 2. NODES
def act_node(state: DevAgentState):
    """Executes the tool (Read/Write/List/Run)."""
    last_message = state["messages"][-1]
    
    # Define complete tool map
    tool_map = {t.name: t for t in all_tools} 
    
    outputs = []
    if last_message.tool_calls:
        print(f"🛠️ EXECUTING TOOLS: {len(last_message.tool_calls)}")
        
        for tool_call in last_message.tool_calls:
            if tool_call["name"] in tool_map:
                try:
                    tool_func = tool_map[tool_call["name"]]
                    print(f"   👉 Running {tool_call['name']}...")
                    res = tool_func.invoke(tool_call["args"])
                    
                    outputs.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"],
                        content=str(res)
                    ))
                except Exception as e:
                    outputs.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"],
                        content=f"Error: {e}"
                    ))
                    
    return {"messages": outputs, "last_status": "acting"}
def reason_node(state: DevAgentState):
    """The Agent decides what to do next."""
    messages = state["messages"]
    
    # Inject Persona if first turn
    if len(messages) == 0 or (len(messages) == 1 and messages[0].type == 'human'):
        sys_msg = SystemMessage(content=(
            f"You are a Senior Software Developer Agent."
            f"You are working in: {settings.ABS_SANDBOX_PATH}."
            f"Always list files first to orient yourself."
            f"Write clean, executable code."
        ))
        messages = [sys_msg] + messages
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response], "last_status": "thinking"}

def act_node(state: DevAgentState):
    """Executes the tool (Read/Write/List)."""
    last_message = state["messages"][-1]
    
    # We construct the Tool execution manually for stability
    outputs = []
    
    if last_message.tool_calls:
        print(f"🛠️ EXECUTING TOOLS: {len(last_message.tool_calls)}")
        tool_map = {t.name: t for t in dev_tools}
        
        for tool_call in last_message.tool_calls:
            if tool_call["name"] in tool_map:
                try:
                    tool_func = tool_map[tool_call["name"]]
                    res = tool_func.invoke(tool_call["args"])
                    
                    outputs.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"],
                        content=str(res)
                    ))
                except Exception as e:
                     outputs.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"],
                        content=f"Error: {e}"
                    ))
                    
    return {"messages": outputs, "last_status": "acting"}

# 3. ROUTER
def should_continue(state: DevAgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "act"
    return "end"


# 4. GRAPH BUILD (Safe Memory Injection)

workflow = StateGraph(DevAgentState)
workflow.add_node("reason", reason_node)
workflow.add_node("act", act_node)
workflow.set_entry_point("reason")
workflow.add_conditional_edges(
    "reason",
    should_continue,
    {
        "act": "act",
        "end": END
    }
)
workflow.add_edge("act", "reason")

# --- SAFE DB CONNECTION ---
# 1. Ensure the 'data' directory exists
db_path = "data/agent_memory.sqlite"
if not os.path.exists("data"):
    os.makedirs("data")

# 2. Connect
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# 3. Compile
dev_graph = workflow.compile(checkpointer=memory)