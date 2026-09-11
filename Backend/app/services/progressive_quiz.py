"""Adaptive MCQ generation service."""

import logging
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langsmith import traceable

from app.core.constants import (
    DEFAULT_DIFFICULTY,
    DIFFICULTY_LEVELS,
    DEFAULT_QUIZ_SIZE,
    MIN_QUIZ_SIZE,
    MAX_QUIZ_SIZE,
    SYSTEM_PROMPT,
)
from app.core.exceptions import AIGenerationError
from app.schemas.studypack import MCQItem

logger = logging.getLogger(__name__)


# ============================================================
# MCQ GENERATION PROMPT
# ============================================================

MCQ_GENERATION_PROMPT = """You are an expert educational assessment designer.

Given the following source material, generate exactly {total_mcqs}
multiple-choice questions (MCQs) at the {difficulty} difficulty level.

Difficulty guidance:
- Easy: recall-level, direct facts
- Medium: application-level, requires understanding
- Hard: analysis/synthesis, requires deep reasoning

Rules:
1. Generate EXACTLY {total_mcqs} questions.
2. Each MCQ must have exactly 4 options.
3. Options must be labeled A, B, C, D.
4. Only one option should be the correct answer.
5. Questions should cover diverse topics from the material.
6. Include a brief explanation for each answer.
7. Assign each question to a relevant topic from the material.
8. The difficulty of every question must be exactly "{difficulty}".
9. Use only information from the source material.
10. Do not generate duplicate questions.

Output Format:
Return ONLY a valid JSON array.

[
  {{
    "id": 1,
    "question": "...",
    "options": [
      "A. ...",
      "B. ...",
      "C. ...",
      "D. ..."
    ],
    "answer": "A. ...",
    "difficulty": "{difficulty}",
    "topic": "...",
    "explanation": "..."
  }}
]

Source Material:
{source_text}

Generate EXACTLY {total_mcqs} MCQs now.
Output ONLY the JSON array.
"""


# ============================================================
# GENERATE MCQs
# ============================================================

@traceable(name="progressive_mcq_generation")
def generate_mcqs(
    text_content: str,
    difficulty: str = DEFAULT_DIFFICULTY,
    quiz_size: int = DEFAULT_QUIZ_SIZE,
    llm=None,
) -> List[MCQItem]:
    """
    Generate a user-selected number of MCQs at the requested
    difficulty level.

    The quiz size is selected by the user and remains the same
    across adaptive quiz rounds.

    Args:
        text_content:
            Source material used to generate questions.

        difficulty:
            Easy, Medium, or Hard.

        quiz_size:
            Number of MCQs requested by the user.

        llm:
            Optional LLM instance. If None, the primary model
            is used.

    Returns:
        List of validated MCQItem objects.

    Raises:
        AIGenerationError:
            If generation, parsing, validation, or AI response
            fails.
    """

    # --------------------------------------------------------
    # Validate source text
    # --------------------------------------------------------

    if not text_content or len(text_content.strip()) < 50:
        raise AIGenerationError(
            "Source text must contain at least 50 characters."
        )

    # --------------------------------------------------------
    # Validate difficulty
    # --------------------------------------------------------

    if difficulty not in DIFFICULTY_LEVELS:
        raise AIGenerationError(
            f"Difficulty must be one of: "
            f"{', '.join(DIFFICULTY_LEVELS)}."
        )

    # --------------------------------------------------------
    # Validate quiz size
    # --------------------------------------------------------

    if not MIN_QUIZ_SIZE <= quiz_size <= MAX_QUIZ_SIZE:
        raise AIGenerationError(
            f"Quiz size must be between "
            f"{MIN_QUIZ_SIZE} and {MAX_QUIZ_SIZE}."
        )

    # --------------------------------------------------------
    # Get LLM
    # --------------------------------------------------------

    if llm is None:
        from app.services.ai_pipeline import get_primary_model

        llm = get_primary_model()

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", MCQ_GENERATION_PROMPT),
    ])

    from app.services.ai_pipeline import normalize_ai_message

    parser = JsonOutputParser()

    chain = prompt | llm | RunnableLambda(normalize_ai_message) | parser

    # --------------------------------------------------------
    # Generate questions
    # --------------------------------------------------------

    try:

        raw_mcqs = chain.invoke({
            "source_text": text_content,
            "total_mcqs": quiz_size,
            "difficulty": difficulty,
        })

        # ----------------------------------------------------
        # Validate AI response format
        # ----------------------------------------------------

        if not isinstance(raw_mcqs, list):
            raise AIGenerationError(
                "AI response must be a JSON array of MCQs."
            )

        # ----------------------------------------------------
        # Validate number of questions
        # ----------------------------------------------------

        if len(raw_mcqs) != quiz_size:
            raise AIGenerationError(
                f"Expected exactly {quiz_size} MCQs, "
                f"but received {len(raw_mcqs)}."
            )

        # ----------------------------------------------------
        # Convert to Pydantic models
        # ----------------------------------------------------

        mcqs: List[MCQItem] = []

        for index, mcq_data in enumerate(raw_mcqs):

            if not isinstance(mcq_data, dict):
                raise AIGenerationError(
                    f"MCQ {index + 1} is not a valid object."
                )

            # Always assign sequential IDs
            mcq_data["id"] = index + 1

            try:
                mcq = MCQItem(**mcq_data)

            except Exception as validation_error:
                raise AIGenerationError(
                    f"Invalid MCQ {index + 1}: "
                    f"{validation_error}"
                )

            mcqs.append(mcq)

        # ----------------------------------------------------
        # Validate difficulty
        # ----------------------------------------------------

        if any(
            mcq.difficulty != difficulty
            for mcq in mcqs
        ):
            raise AIGenerationError(
                f"All generated MCQs must have "
                f"{difficulty} difficulty."
            )

        # ----------------------------------------------------
        # Final count validation
        # ----------------------------------------------------

        if len(mcqs) != quiz_size:
            raise AIGenerationError(
                f"Expected {quiz_size} MCQs, "
                f"received {len(mcqs)}."
            )

        logger.info(
            "Generated %s %s MCQs successfully.",
            len(mcqs),
            difficulty,
        )

        return mcqs

    # --------------------------------------------------------
    # Handle generation errors
    # --------------------------------------------------------

    except AIGenerationError:
        raise

    except Exception as e:

        logger.exception(
            "MCQ generation failed."
        )

        raise AIGenerationError(
            f"Failed to generate MCQs: {str(e)}"
        )