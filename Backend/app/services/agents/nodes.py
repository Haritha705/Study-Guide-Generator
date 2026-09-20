from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.services.ai_pipeline import get_primary_model
from app.services.agents.state import AgentState
from app.services.agents.tools import retrieve_notes_tool, generate_quiz_tool, search_books_tool, search_videos_tool
import json

class RouteInfo(BaseModel):
    next_agent: str = Field(description="The name of the next agent to route to. Can be 'RAG', 'Quiz', 'Tutor', 'Resource', or 'FINISH'")

def supervisor_node(state: AgentState):
    llm = get_primary_model().with_structured_output(RouteInfo)
    
    system_prompt = """You are a Supervisor routing student requests to specialized AI agents.
Available Agents:
- RAG: Specialized in extracting and summarizing core concepts from uploaded PDF notes.
- Quiz: Specialized in testing the student's knowledge and generating adaptive MCQs.
- Tutor: Specialized in answering questions, giving analogies, and chatting about a concept.
- Resource: Specialized in finding external YouTube videos or Google Books for topics.

Analyze the user's latest message and return the next_agent. If the request has been fully resolved, return 'FINISH'."""
    
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    
    try:
        route = llm.invoke(messages)
        next_agent = route.next_agent
    except Exception as e:
        next_agent = "Tutor" # fallback
        
    return {"next_agent": next_agent}

def rag_agent_node(state: AgentState):
    llm = get_primary_model().bind_tools([retrieve_notes_tool])
    context = state.get("context") or "No document context available."
    system_prompt = f"You are the RAG Agent. Use your tools to retrieve notes and summarize them. Here is the current document context/summary:\n\n{context}"
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}

def quiz_agent_node(state: AgentState):
    llm = get_primary_model().bind_tools([retrieve_notes_tool, generate_quiz_tool])
    context = state.get("context") or "No document context available."
    system_prompt = f"You are the Quiz Agent. You can retrieve notes and generate quizzes to test the user's knowledge. Current document context:\n\n{context}"
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}

def tutor_agent_node(state: AgentState):
    llm = get_primary_model().bind_tools([retrieve_notes_tool])
    context = state.get("context") or "No document context available."
    system_prompt = f"You are the Tutor Agent. You answer questions and explain concepts using simple analogies. Always retrieve context from notes first. Current document context:\n\n{context}"
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}

def resource_agent_node(state: AgentState):
    llm = get_primary_model().bind_tools([search_books_tool, search_videos_tool])
    context = state.get("context") or "No document context available."
    system_prompt = f"You are the Resource Agent. Use tools to find external books and videos. Current document context:\n\n{context}"
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}
