"""
StudyPack Resource Service — Central aggregator for external educational resources.

CRITICAL ARCHITECTURE PRINCIPLE:
External resources (Google Books & YouTube) are strictly supplementary.
They MUST NOT be used as factual grounding for core StudyPack generation
(summary, notes, MCQs, short answers, glossary, study order).
The user's uploaded syllabus or lecture notes remain the ONLY grounding source.
"""

import logging
from typing import Any, Dict, List

from app.services.study_pack.books_service import search_books
from app.services.study_pack.youtube_service import search_educational_videos

logger = logging.getLogger(__name__)


def get_study_resources(
    topic: str,
    max_books: int = 5,
    max_videos: int = 5,
) -> Dict[str, Any]:
    """
    Aggregate supplementary learning resources (books and videos) for a given topic.

    Isolates external service failures so that if one provider fails or exhausts
    quotas, the other provider's results are still returned cleanly.
    """
    clean_topic = topic.strip() if topic else ""
    if not clean_topic:
        return {
            "topic": "",
            "books": [],
            "videos": [],
        }

    # Fetch books
    try:
        books = search_books(query=clean_topic, max_results=max_books)
    except Exception as exc:
        logger.error("Error fetching books in resource aggregator: %s", exc)
        books = []

    # Fetch videos
    try:
        videos = search_educational_videos(topic=clean_topic, max_results=max_videos)
    except Exception as exc:
        logger.error("Error fetching videos in resource aggregator: %s", exc)
        videos = []

    return {
        "topic": clean_topic,
        "books": books,
        "videos": videos,
    }
