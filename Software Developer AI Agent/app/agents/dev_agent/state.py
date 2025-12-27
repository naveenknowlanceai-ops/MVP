from typing import TypedDict, List, Annotated
import operator
from langchain_core.messages import BaseMessage

class DevAgentState(TypedDict):
    """
    State for the Software Developer.
    Matches LangGraph 0.1.5 standards.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    current_task: str
    file_context: str
    last_status: str