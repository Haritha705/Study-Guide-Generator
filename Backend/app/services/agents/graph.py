from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.services.agents.state import AgentState
from app.services.agents.nodes import (
    supervisor_node,
    rag_agent_node,
    quiz_agent_node,
    tutor_agent_node,
    resource_agent_node
)
from app.services.agents.tools import retrieve_notes_tool, generate_quiz_tool, search_books_tool, search_videos_tool

def build_graph():
    builder = StateGraph(AgentState)
    
    # Add Nodes
    builder.add_node("Supervisor", supervisor_node)
    builder.add_node("RAG", rag_agent_node)
    builder.add_node("Quiz", quiz_agent_node)
    builder.add_node("Tutor", tutor_agent_node)
    builder.add_node("Resource", resource_agent_node)
    
    # Tool Node
    tools = [retrieve_notes_tool, generate_quiz_tool, search_books_tool, search_videos_tool]
    tool_node = ToolNode(tools)
    builder.add_node("tools", tool_node)
    
    # Entry Point
    builder.set_entry_point("Supervisor")
    
    # Supervisor routing function
    def router(state: AgentState):
        agent = state.get("next_agent", "FINISH")
        if agent == "FINISH":
            return END
        if agent in ["RAG", "Quiz", "Tutor", "Resource"]:
            return agent
        return END

    # Supervisor Edges
    builder.add_conditional_edges("Supervisor", router)
    
    # Agent Tool Routing
    def agent_router(state: AgentState):
        messages = state.get("messages", [])
        if messages and messages[-1].tool_calls:
            return "tools"
        return END
        
    builder.add_conditional_edges("RAG", agent_router, {"tools": "tools", END: END})
    builder.add_conditional_edges("Quiz", agent_router, {"tools": "tools", END: END})
    builder.add_conditional_edges("Tutor", agent_router, {"tools": "tools", END: END})
    builder.add_conditional_edges("Resource", agent_router, {"tools": "tools", END: END})
    
    # Tool Edge returns to Supervisor to decide next steps or finish
    builder.add_edge("tools", "Supervisor")
    
    return builder

# pyrefly: ignore [missing-import]
from langgraph.checkpoint.sqlite import SqliteSaver

# Use a separate database file for checkpoints
memory = SqliteSaver.from_conn_string("langgraph_checkpoints.db")
agent_executor = build_graph().compile(checkpointer=memory)
