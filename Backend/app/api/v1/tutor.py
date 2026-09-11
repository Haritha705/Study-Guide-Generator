"""RAG AI Tutor API endpoint — context-grounded Q&A."""

from fastapi import APIRouter, HTTPException

from app.schemas.tutor import TutorRequest, TutorResponse, SourceChunk
from app.services.rag.retriever import retrieve_context, retrieve_context_with_scores
from app.core.exceptions import RAGRetrievalError
from app.core.constants import SYSTEM_PROMPT

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
        # Retrieve scored context chunks
        scored_chunks = retrieve_context_with_scores(request.question, top_k=4)

        # Build context string
        context = retrieve_context(request.question, top_k=4)

        # If no context is available, provide a helpful response
        if not context:
            return TutorResponse(
                answer=(
                    "I don't have any study material loaded to reference. "
                    "Please upload a PDF or paste text first, then ask your question again."
                ),
                sources=[],
                confidence=0.0,
                follow_up_suggestions=[
                    "Upload a PDF document first",
                    "Paste your study material as text",
                ],
            )

        # Generate answer using the primary LLM with retrieved context
        from langchain_core.prompts import ChatPromptTemplate
        from app.services.ai_pipeline import get_primary_model

        llm = get_primary_model()

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{SYSTEM_PROMPT}\n\n"
                       "You are a tutor answering student questions STRICTLY based on "
                       "the provided context. If the context doesn't contain the answer, "
                       "say so clearly. Do not make up information.\n\n"
                       "Also suggest 2-3 follow-up questions the student might want to ask."),
            ("human", "**Context from study material:**\n{context}\n\n"
                      "**Student's question:** {question}\n\n"
                      "Answer the question based on the context above. "
                      "End with a section '## Follow-up Questions' listing 2-3 suggestions."),
        ])

        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "question": request.question,
        })

        raw_content = response.content if hasattr(response, "content") else str(response)
        # gemini-3.6-flash returns content as a list of dicts
        if isinstance(raw_content, list):
            answer_text = "".join(
                part["text"] for part in raw_content
                if isinstance(part, dict) and "text" in part
            )
        else:
            answer_text = raw_content

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
