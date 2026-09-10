import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_mistralai.embeddings import MistralAIEmbeddings
from schemas import StudyPackOutput
from langsmith import traceable

load_dotenv()

# Dual Provider Router Setup
def get_primary_model():
    # Claude API (claude-3-5-sonnet) for complex reasoning and structured output
    return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.2)

def get_secondary_model():
    # Mistral API (mistral-large) for fast extraction and preprocessing
    return ChatMistralAI(model="mistral-large-latest", temperature=0.1)

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
                   "You must output STRICTLY in the following JSON format.\n"
                   "{format_instructions}"),
        ("human", "Here is the source material:\n\n{source_text}\n\nGenerate the study pack now.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt | primary_llm | parser
    
    # Execute chain (tracked by LangSmith implicitly via environment variables)
    result = chain.invoke({"source_text": text_content})
    return result
