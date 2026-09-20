"""RAG AI Tutor API endpoint — context-grounded Q&A."""

import logging
from fastapi import APIRouter, HTTPException

from app.schemas.tutor import TutorRequest, TutorResponse, SourceChunk
from app.services.rag.retriever import retrieve_context, retrieve_context_with_scores
from app.core.exceptions import RAGRetrievalError
from app.core.constants import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ask", response_model=TutorResponse)
async def ask_tutor(request: TutorRequest):
    """
    Ask the AI tutor a question grounded in the uploaded study material.

    The tutor retrieves relevant context from the RAG vector store
    and generates a bounded answer. If no document has been indexed,
    the tutor will indicate that context is unavailable.
    """
    if not request.question or len(request.question.strip()) < 5:
        raise HTTPException(status_code=400, detail="Question must be at least 5 characters.")

    try:
        # 1. If context_text is provided, auto-index into vector store if uninitialized
        if request.context_text and request.context_text.strip():
            from app.services.rag.vector_store import vector_store_manager
            if not vector_store_manager.is_initialized:
                try:
                    from app.services.rag.retriever import index_document
                    index_document(request.context_text)
                except Exception as idx_err:
                    logger.warning("Auto-indexing context_text encountered: %s", idx_err)

        # 2. Retrieve context from vector store
        scored_chunks = []
        context = ""
        try:
            scored_chunks = retrieve_context_with_scores(request.question, top_k=4)
            context = retrieve_context(request.question, top_k=4)
        except Exception as ret_err:
            logger.warning("RAG context retrieval encountered: %s", ret_err)

        # 3. Fallback to direct client context if vector search returned nothing
        if not context and request.context_text and request.context_text.strip():
            context = request.context_text[:15000]
            scored_chunks = [
                {"text": "Study pack notes, summary, and glossary", "relevance_score": 0.95}
            ]
        elif context and request.context_text and len(context) < 1000:
            context = f"{context}\n\n**Pack Notes & Glossary:**\n{request.context_text[:5000]}"

        # If absolutely no context is available anywhere
        if not context or not context.strip():
            return TutorResponse(
                answer=(
                    "I don't have study material loaded for this topic yet. "
                    "Please open a study pack or upload lecture notes, and I will gladly answer all your questions!"
                ),
                sources=[],
                confidence=0.0,
                follow_up_suggestions=[
                    "What are the main concepts in this subject?",
                    "Can you generate practice questions?",
                ],
            )

        # 4. Generate answer using primary LLM with secondary fallback
        from langchain_core.prompts import ChatPromptTemplate
        from app.services.ai_pipeline import get_primary_model, get_secondary_model, normalize_ai_message

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{SYSTEM_PROMPT}\n\n"
                       "You are an expert AI Study Tutor answering student questions based on "
                       "the provided study material and lecture notes.\n"
                       "Provide clear, pedagogically sound, encouraging, and detailed answers.\n"
                       "Always explain concepts thoroughly, citing definitions and terms from the notes where applicable.\n"
                       "End your answer with a section titled '## Follow-up Questions' with 2-3 helpful suggestions."),
            ("human", "**Context from study material:**\n{context}\n\n"
                      "**Student's question:** {question}\n\n"
                      "Please answer the question clearly and thoroughly."),
        ])

        response = None
        for candidate in ["gemini-flash-lite-latest", "gemini-3.5-flash-lite"]:
            try:
                llm = get_primary_model(candidate)
                chain = prompt | llm
                response = chain.invoke({"context": context, "question": request.question})
                break
            except Exception as model_err:
                logger.warning("Tutor Gemini model %s failed: %s", candidate, model_err)

        if response is None:
            logger.info("Trying Mistral fallback for AI tutor...")
            try:
                mistral_llm = get_secondary_model()
                chain = prompt | mistral_llm
                response = chain.invoke({"context": context, "question": request.question})
            except Exception as mistral_err:
                logger.error("Tutor Mistral fallback also failed: %s", mistral_err)
                raise HTTPException(
                    status_code=503,
                    detail="AI tutor is temporarily busy. Please try asking your question again in a moment.",
                )

        raw_content = response.content if hasattr(response, "content") else str(response)
        if isinstance(raw_content, list):
            answer_text = "".join(
                part["text"] for part in raw_content
                if isinstance(part, dict) and "text" in part
            )
        else:
            answer_text = str(raw_content)


        # Parse follow-up suggestions from the answer
        follow_ups = []
        if "## Follow-up Questions" in answer_text:
            parts = answer_text.split("## Follow-up Questions")
            answer_text = parts[0].strip()
            follow_up_section = parts[1].strip()
            for line in follow_up_section.split("\n"):
                line = line.strip().lstrip("-").lstrip("•").lstrip("0123456789.").strip()
                if line and len(line) > 5:
                    follow_ups.append(line)

        # Build source chunks for transparency
        sources = [
            SourceChunk(text=chunk["text"], relevance_score=chunk["relevance_score"])
            for chunk in scored_chunks
        ]

        # Estimate confidence from average relevance
        avg_relevance = (
            sum(c["relevance_score"] for c in scored_chunks) / len(scored_chunks)
            if scored_chunks else 0.0
        )

        return TutorResponse(
            answer=answer_text,
            sources=sources,
            confidence=min(avg_relevance, 1.0),
            follow_up_suggestions=follow_ups[:3],
        )

    except RAGRetrievalError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tutor failed: {str(e)}")
