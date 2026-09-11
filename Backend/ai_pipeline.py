# app/services/ai_pipeline.py

from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# pyrefly: ignore [missing-import]
from app.core.config import settings
from app.core.constants import (
    DEFAULT_QUIZ_SIZE,
    MIN_QUIZ_SIZE,
    MAX_QUIZ_SIZE,
)
from app.schemas.studypack import StudyPackOutput


# ============================================================
# PRIMARY AI MODEL - GEMINI
# ============================================================

def get_primary_model():
    """
    Returns the primary Gemini model.
    """

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )


# ============================================================
# SECONDARY AI MODEL - MISTRAL
# ============================================================

def get_secondary_model():
    """
    Returns the secondary Mistral model.
    """

    return ChatMistralAI(
        model="open-mixtral-8x7b",
        api_key=settings.MISTRAL_API_KEY,
        temperature=0.3,
    )


# ============================================================
# STUDY PACK PROMPT
# ============================================================

STUDY_PACK_PROMPT = """
You are an expert AI tutor and study-material generator.

Analyze the following educational content and create a complete
study pack for a college student.

SOURCE CONTENT:
{text_content}

Generate the following:

1. SUMMARY
   - Give a clear and concise overall summary.
   - Cover the important concepts.

2. NOTES
   - Divide the content into logical topics.
   - Each topic should contain useful bullet-point notes.
   - Identify important concepts and definitions.
   - Add highlights where appropriate.

3. MCQs
   - Generate EXACTLY {quiz_size} multiple-choice questions.
   - Initial difficulty must be Medium.
   - Each question must have exactly 4 options.
   - Only one option must be correct.
   - Provide an explanation for every answer.
   - Assign the appropriate topic.
   - Difficulty must be exactly "Medium".

4. SHORT ANSWER QUESTIONS
   - Generate 5 short-answer questions.
   - Provide a model answer for every question.
   - Cover important concepts from the source.
   - Use a mixture of conceptual and understanding-based questions.

5. FLASHCARDS
   - Generate useful term-definition flashcards.
   - Focus on important concepts and terminology.

6. GLOSSARY
   - Extract important technical terms.
   - Give a simple and accurate definition for each term.

7. RECOMMENDED STUDY ORDER
   - Arrange the topics from foundational concepts to advanced concepts.

IMPORTANT:
- Use ONLY the information available in the source content.
- Do not invent topics that are unrelated to the source.
- Return the result in the exact JSON structure required by the schema.
"""


# ============================================================
# GENERATE COMPLETE STUDY PACK
# ============================================================

def generate_study_pack(
    text_content: str,
    quiz_size: int = DEFAULT_QUIZ_SIZE,
    llm=None,
) -> StudyPackOutput:

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not text_content or len(text_content.strip()) < 50:
        raise ValueError(
            "Source text must contain at least 50 characters."
        )

    # --------------------------------------------------------
    # Validate user-selected quiz size
    # --------------------------------------------------------

    if not MIN_QUIZ_SIZE <= quiz_size <= MAX_QUIZ_SIZE:
        raise ValueError(
            f"Quiz size must be between "
            f"{MIN_QUIZ_SIZE} and {MAX_QUIZ_SIZE}."
        )

    # --------------------------------------------------------
    # Get AI model
    # --------------------------------------------------------

    if llm is None:
        llm = get_primary_model()

    # --------------------------------------------------------
    # Create prompt
    # --------------------------------------------------------

    prompt = ChatPromptTemplate.from_template(
        STUDY_PACK_PROMPT
    )

    parser = JsonOutputParser(
        pydantic_object=StudyPackOutput
    )

    chain = prompt | llm | parser

    # --------------------------------------------------------
    # Generate study pack
    # --------------------------------------------------------

    result = chain.invoke(
        {
            "text_content": text_content,
            "quiz_size": quiz_size,
        }
    )

    # --------------------------------------------------------
    # Convert to Pydantic schema
    # --------------------------------------------------------

    study_pack = StudyPackOutput.model_validate(result)

    # --------------------------------------------------------
    # Validate MCQ count
    # --------------------------------------------------------

    if len(study_pack.mcqs) != quiz_size:
        raise ValueError(
            f"AI generated {len(study_pack.mcqs)} MCQs, "
            f"but {quiz_size} were requested."
        )

    # --------------------------------------------------------
    # Validate MCQ difficulty
    # --------------------------------------------------------

    for mcq in study_pack.mcqs:

        if mcq.difficulty != "Medium":
            raise ValueError(
                "Initial study-pack MCQs must have Medium difficulty."
            )

    return study_pack