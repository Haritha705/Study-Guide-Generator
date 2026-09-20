from langchain_core.tools import tool
from app.services.progressive_quiz import generate_mcqs
from app.services.rag.retriever import retrieve_context
from app.services.study_pack.books_service import search_books
from app.services.study_pack.youtube_service import search_educational_videos
import json

@tool
def retrieve_notes_tool(query: str) -> str:
    """Retrieve relevant information from the uploaded study material based on a query."""
    try:
        context = retrieve_context(query, top_k=3)
        if not context:
            return "No relevant notes found in the study material."
        return context
    except Exception as e:
        return f"Error retrieving notes: {str(e)}"

@tool
def generate_quiz_tool(topic: str, difficulty: str = "Medium", num_questions: int = 5) -> str:
    """Generate multiple-choice questions for a specific topic."""
    try:
        mcqs = generate_mcqs(text_content=topic, difficulty=difficulty, quiz_size=num_questions)
        return json.dumps([mcq.model_dump() for mcq in mcqs], indent=2)
    except Exception as e:
        return f"Error generating quiz: {str(e)}"

@tool
def search_books_tool(topic: str) -> str:
    """Search for educational books related to a topic."""
    try:
        books = search_books(topic, max_results=3)
        return json.dumps(books, indent=2)
    except Exception as e:
        return f"Error finding books: {str(e)}"

@tool
def search_videos_tool(topic: str) -> str:
    """Search for educational YouTube videos related to a topic."""
    try:
        videos = search_educational_videos(topic, max_results=3)
        return json.dumps(videos, indent=2)
    except Exception as e:
        return f"Error finding videos: {str(e)}"
