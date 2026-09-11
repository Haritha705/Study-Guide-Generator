import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore [missing-import]

# pyrefly: ignore [missing-import]
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import InMemoryVectorStore
# pyrefly: ignore [missing-import]
from langchain_mistralai.embeddings import MistralAIEmbeddings
from app.schemas.studypack import StudyPackOutput
from app.core.constants import DEFAULT_DIFFICULTY, DEFAULT_QUIZ_SIZE
from app.core.exceptions import AIGenerationError
from app.config import settings
from langsmith import traceable

load_dotenv()


def normalize_ai_message(message):
    """Extract plain text from AIMessage.content.

    gemini-3.6-flash (via langchain-google-genai 4.4+) returns
    content as a list of dicts, e.g.:
        [{'type': 'text', 'text': '...', 'extras': {...}}]
    instead of a plain string.  This normalizer converts back
    to a plain-string AIMessage so downstream parsers work.
    """
    content = message.content
    if isinstance(content, list):
        text = "".join(
            part["text"] for part in content
            if isinstance(part, dict) and "text" in part
        )
        message.content = text
    return message


# Dual Provider Router Setup
def get_primary_model():
    # Gemini API (gemini-3.6-flash) for complex reasoning and structured output
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=settings.GEMINI_API_KEY,
    )

def get_secondary_model():
    # Mistral API (open-mixtral-8x7b) for fast extraction and preprocessing
    return ChatMistralAI(model="open-mixtral-8x7b", temperature=0.1)

def get_embeddings_model():
    return MistralAIEmbeddings(model="mistral-embed")

@traceable(name="rag_chunking_pipeline")
def build_vector_store(text_content: str):
    # RAG: Construct chunking pipeline
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text_content)
    
    embeddings = get_embeddings_model()
    # In-memory vector store for fast retrieval
    vector_store = InMemoryVectorStore.from_texts(chunks, embeddings)
    return vector_store.as_retriever()

@traceable(name="study_pack_generation")
def generate_study_pack(text_content: str) -> StudyPackOutput:
    """Orchestrates the generation of structured study materials."""
    
    # 1. We could use Mistral for summarizing or chunking if it was massive.
    # But for structured JSON matching our strict schema, we use Claude.
    
    primary_llm = get_primary_model()
    parser = PydanticOutputParser(pydantic_object=StudyPackOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert educational AI tutor. Analyze the provided lecture notes/syllabus and generate a comprehensive study pack.\n\n"
                   f"The response must begin with a concise summary. Generate exactly {DEFAULT_QUIZ_SIZE} MCQs, all at {DEFAULT_DIFFICULTY} difficulty, "
                   "and include short-answer questions and glossary flashcards.\n\n"
                   "You must output STRICTLY in the following JSON format.\n"
                   "{format_instructions}"),
        ("human", "Here is the source material:\n\n{source_text}\n\nGenerate the study pack now.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | primary_llm | RunnableLambda(normalize_ai_message) | parser
    
    # Execute chain (tracked by LangSmith implicitly via environment variables)
    try:
        result = chain.invoke({"source_text": text_content})
    except Exception as exc:
        raise AIGenerationError(f"Failed to generate study pack: {exc}") from exc

    if not result.summary.strip():
        raise AIGenerationError("Generated study pack is missing a summary.")
    if len(result.mcqs) != DEFAULT_QUIZ_SIZE:
        raise AIGenerationError(
            f"Generated study pack must contain exactly {DEFAULT_QUIZ_SIZE} MCQs."
        )
    if any(mcq.difficulty != DEFAULT_DIFFICULTY for mcq in result.mcqs):
        raise AIGenerationError(
            f"Study-pack MCQs must all have {DEFAULT_DIFFICULTY} difficulty."
        )
    if not result.flashcards:
        raise AIGenerationError("Generated study pack is missing glossary flashcards.")

    return result
