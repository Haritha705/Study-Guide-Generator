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


import logging
import time

logger = logging.getLogger(__name__)

# Fallback pool: stable production models first, followed by alternates
CANDIDATE_GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.6-flash",
]

# Dual Provider Router Setup
def get_primary_model(model_name: str = "gemini-flash-lite-latest"):
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY,
        request_timeout=120.0,
        max_retries=2,
    )

def get_secondary_model(model_name: str = "mistral-small-latest"):
    """Mistral AI model for extraction and automatic failover."""
    key = (getattr(settings, "MISTRAL_API_KEY", "") or os.getenv("MISTRAL_API_KEY", "")).strip()
    return ChatMistralAI(
        model=model_name,
        mistral_api_key=key,
        temperature=0.1,
    )

def get_embeddings_model():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    gemini_key = getattr(settings, "GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        return GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=gemini_key,
        )
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
    """Orchestrates study materials generation with immediate Mistral fallback on Gemini busy."""
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
    safe_text = text_content[:200000] if len(text_content) > 200000 else text_content

    # ── 1. Primary: Stable Gemini Flash ──────────────────────────────────────
    try:
        logger.info("Attempting study pack generation using Gemini (gemini-flash-latest)...")
        gemini_llm = get_primary_model("gemini-flash-latest")
        chain = prompt | gemini_llm | RunnableLambda(normalize_ai_message) | parser
        result = chain.invoke({"source_text": safe_text})
        if result and result.summary.strip():
            logger.info("Study pack generated successfully with Gemini.")
            return result
    except Exception as gemini_err:
        logger.warning(
            "Gemini returned error (%s). Falling back immediately to Mistral AI...",
            str(gemini_err)[:180],
        )

    # ── 2. Immediate Secondary Fallback: Mistral AI ───────────────────────────
    mistral_key = (getattr(settings, "MISTRAL_API_KEY", "") or os.getenv("MISTRAL_API_KEY", "")).strip()
    if mistral_key:
        for mistral_model in ["mistral-small-latest", "ministral-8b-latest"]:
            try:
                logger.info("Attempting generation using Mistral fallback (%s)...", mistral_model)
                mistral_llm = get_secondary_model(mistral_model)
                chain = prompt | mistral_llm | RunnableLambda(normalize_ai_message) | parser
                result = chain.invoke({"source_text": safe_text})
                if result and result.summary.strip():
                    logger.info("Study pack generated successfully with Mistral fallback (%s)!", mistral_model)
                    return result
            except Exception as mistral_err:
                logger.warning("Mistral (%s) failed: %s", mistral_model, str(mistral_err)[:180])

    # ── 3. Tertiary Retry: Alternate Gemini Endpoints ─────────────────────────
    for alt_model in ["gemini-3.5-flash", "gemini-3.7-flash"]:
        try:
            logger.info("Retrying with alternate Gemini model (%s)...", alt_model)
            time.sleep(2)
            alt_llm = get_primary_model(alt_model)
            chain = prompt | alt_llm | RunnableLambda(normalize_ai_message) | parser
            result = chain.invoke({"source_text": safe_text})
            if result and result.summary.strip():
                return result
        except Exception as alt_err:
            logger.warning("Alternate model %s also failed: %s", alt_model, str(alt_err)[:180])

    raise AIGenerationError(
        "All AI providers (Gemini & Mistral) are currently experiencing high demand. Please try again in a few moments."
    )

