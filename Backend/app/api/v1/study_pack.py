"""API endpoints for StudyPack external educational resources (Google Books & YouTube)."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.resources import (
    BooksResponse,
    VideosResponse,
    StudyPackResourcesResponse,
)
from app.services.study_pack.books_service import search_books
from app.services.study_pack.youtube_service import search_educational_videos
from app.services.study_pack.resource_service import get_study_resources

router = APIRouter()


@router.get("/books", response_model=BooksResponse)
async def get_books(
    topic: str = Query(..., min_length=1, description="Topic to search for relevant books"),
    max_results: int = Query(default=5, ge=1, le=5, description="Max books to return (up to 5)"),
):
    """
    Search Google Books Volumes API for supplementary educational books.
    Never invents books or fake metadata.
    """
    clean_topic = topic.strip()
    if not clean_topic:
        raise HTTPException(status_code=400, detail="Topic parameter cannot be empty.")

    books = search_books(query=clean_topic, max_results=max_results)
    return BooksResponse(topic=clean_topic, books=books)


@router.get("/videos", response_model=VideosResponse)
async def get_videos(
    topic: str = Query(..., min_length=1, description="Topic to search for educational videos"),
    max_results: int = Query(default=5, ge=1, le=5, description="Max videos to return (up to 5)"),
):
    """
    Search YouTube Data API v3 for relevant educational videos and lectures.
    Constructs direct watch URLs and cleans HTML entities.
    """
    clean_topic = topic.strip()
    if not clean_topic:
        raise HTTPException(status_code=400, detail="Topic parameter cannot be empty.")

    videos = search_educational_videos(topic=clean_topic, max_results=max_results)
    return VideosResponse(topic=clean_topic, videos=videos)


@router.get("/resources", response_model=StudyPackResourcesResponse)
async def get_all_resources(
    topic: str = Query(..., min_length=1, description="Topic for combined study resources"),
    max_books: int = Query(default=5, ge=1, le=5),
    max_videos: int = Query(default=5, ge=1, le=5),
):
    """
    Combined educational resources (books and videos) for a study topic.
    """
    clean_topic = topic.strip()
    if not clean_topic:
        raise HTTPException(status_code=400, detail="Topic parameter cannot be empty.")

    resources = get_study_resources(topic=clean_topic, max_books=max_books, max_videos=max_videos)
    return StudyPackResourcesResponse(**resources)
