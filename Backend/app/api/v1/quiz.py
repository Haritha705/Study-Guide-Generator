"""Quiz API endpoints — submission, grading, and generation."""

from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Optional

from app.schemas.quiz import QuizSubmission, QuizResult
from app.schemas.studypack import MCQItem
from app.services.analytics_engine import evaluate_quiz
from app.services.progressive_quiz import generate_mcqs
from app.core.exceptions import QuizEvaluationError, AIGenerationError

router = APIRouter()


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    """
    Submit quiz answers for grading.

    The request must include either:
    - `mcqs` field with the original MCQ items (for server-side grading), or
    - The MCQs are looked up from the study pack by `studypack_id`.

    Returns a graded QuizResult with score, weak topics, and difficulty breakdown.
    """
    if not submission.answers:
        raise HTTPException(status_code=400, detail="No answers provided.")

    if not submission.mcqs:
        raise HTTPException(
            status_code=400,
            detail="MCQ items must be provided for grading. "
                   "Include the 'mcqs' field in your submission."
        )

    try:
        # Convert raw MCQ dicts to MCQItem models
        mcq_items = [MCQItem(**mcq) for mcq in submission.mcqs]
        result = evaluate_quiz(submission, mcq_items)
        return result
    except QuizEvaluationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz evaluation failed: {str(e)}")


@router.post("/generate")
async def generate_quiz(
    text_content: str = Body(..., embed=True),
    difficulty: str = Body("Medium", embed=True),
    quiz_size: Optional[int] = Body(None, embed=True),
):
    """
    Generate MCQs from source text at the requested difficulty (Easy, Medium, Hard).
    The client can also specify quiz_size (e.g. 5, 10, 15).
    """
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Source text must be at least 50 characters."
        )

    try:
        kwargs = {"difficulty": difficulty}
        if quiz_size is not None and quiz_size > 0:
            kwargs["quiz_size"] = quiz_size
        mcqs = generate_mcqs(text_content, **kwargs)
        return {"mcqs": [mcq.model_dump() for mcq in mcqs]}
    except AIGenerationError as e:
        raise HTTPException(status_code=502, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
