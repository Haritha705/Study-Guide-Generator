import operator
from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """The state of the multi-agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_agent: Optional[str]
    context: Optional[str]
    current_study_pack_id: Optional[str]
