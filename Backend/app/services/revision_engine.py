"""Revision engine — generates focused revision material from notes and missed questions."""

import logging
from typing import List, Dict, Any, Optional

from app.schemas.studypack import NoteItem, MCQItem

logger = logging.getLogger(__name__)

# Highlight types that are always included in revision material
REVISION_HIGHLIGHT_TYPES = {"Important", "Definition", "Remember"}


def generate_revision_material(
    notes: List[Dict[str, Any]],
    missed_questions: Optional[List[Dict[str, Any]]] = None,
    mcqs: Optional[List[Dict[str, Any]]] = None,
    missed_question_ids: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Generate focused revision material by extracting:
    1. Important/Definition/Remember callouts from notes.
    2. Missed quiz questions for review.
    3. Key formulas and concepts.

    Args:
        notes: List of note dicts (matching NoteItem schema).
        missed_questions: Pre-filtered list of missed MCQ dicts (legacy param).
        mcqs: Full list of MCQ dicts; used with missed_question_ids to filter.
        missed_question_ids: IDs of missed questions to extract from mcqs.

    Returns:
        Dictionary with revision highlights, review questions, and topic summaries.
    """
    highlights = []
    key_definitions = []
    topic_summaries = []

    # --- Extract highlights from notes ---
    for note in notes:
        topic = note.get("topic", "Unknown Topic")
        note_highlights = note.get("highlights", [])

        topic_key_points = []

        for hl in note_highlights:
            hl_type = hl.get("type", "")
            hl_text = hl.get("text", "")

            if hl_type in REVISION_HIGHLIGHT_TYPES:
                highlights.append({
                    "type": hl_type,
                    "text": hl_text,
                    "topic": topic,
                })

            if hl_type == "Definition":
                key_definitions.append({
                    "term": hl_text.split(":")[0].strip() if ":" in hl_text else topic,
                    "definition": hl_text,
                    "topic": topic,
                })

            if hl_type in {"Important", "Remember"}:
                topic_key_points.append(hl_text)

        if topic_key_points:
            topic_summaries.append({
                "topic": topic,
                "key_points": topic_key_points,
            })

    # --- Extract missed questions for review ---
    review_questions = []

    if missed_questions:
        review_questions = missed_questions
    elif mcqs and missed_question_ids:
        for mcq in mcqs:
            if mcq.get("id") in missed_question_ids:
                review_questions.append({
                    "id": mcq["id"],
                    "question": mcq.get("question", ""),
                    "correct_answer": mcq.get("answer", ""),
                    "explanation": mcq.get("explanation", ""),
                    "topic": mcq.get("topic", ""),
                    "difficulty": mcq.get("difficulty", ""),
                })

    revision_pack = {
        "highlights": highlights,
        "key_definitions": key_definitions,
        "topic_summaries": topic_summaries,
        "review_questions": review_questions,
        "total_highlights": len(highlights),
        "total_review_questions": len(review_questions),
    }

    logger.info(
        f"Revision material generated: {len(highlights)} highlights, "
        f"{len(review_questions)} review questions."
    )
    return revision_pack
