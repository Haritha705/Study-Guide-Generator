from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.agents.graph import agent_executor
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    study_pack_id: Optional[str] = None
    context_text: Optional[str] = None

class AgentResponse(BaseModel):
    response: str
    
@router.post("/chat", response_model=AgentResponse)
def chat_with_agent(request: AgentRequest):
    """
    Unified endpoint to interact with the LangGraph multi-agent system.
    """
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query is too short.")
        
    try:
        inputs = {
            "messages": [HumanMessage(content=request.query)],
            "context": request.context_text,
            "current_study_pack_id": request.study_pack_id
        }
        
        # Set up checkpointer config with thread_id for memory
        thread_id = request.study_pack_id if request.study_pack_id else "default_session"
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the LangGraph workflow
        output_state = agent_executor.invoke(inputs, config=config)
        
        # Get the last message in the state
        messages = output_state.get("messages", [])
        if messages:
            content = messages[-1].content
            if isinstance(content, list):
                final_message = "".join(
                    part["text"] for part in content
                    if isinstance(part, dict) and "text" in part
                )
            else:
                final_message = str(content)
        else:
            final_message = "I couldn't generate a response."
            
        return AgentResponse(response=final_message)
        
    except Exception as e:
        logger.exception("Agent workflow failed")
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")
