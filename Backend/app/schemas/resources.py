from typing import List, Optional
from pydantic import BaseModel, Field


class BookItem(BaseModel):
    """Normalized educational book item from Google Books API."""
    title: str = Field(default="", description="Title of the book")
    authors: List[str] = Field(default_factory=list, description="List of book authors")
    publisher: Optional[str] = Field(default="", description="Publisher name")
    publishedDate: Optional[str] = Field(default="", description="Publication date string")
    description: Optional[str] = Field(default="", description="Book summary or description")
    thumbnail: Optional[str] = Field(default="", description="URL of the book cover thumbnail")
    previewLink: Optional[str] = Field(default="", description="Google Books preview link")
    infoLink: Optional[str] = Field(default="", description="Google Books info link")
    categories: List[str] = Field(default_factory=list, description="Subject categories")


class BooksResponse(BaseModel):
    """API response model for book search."""
    topic: str
    books: List[BookItem] = Field(default_factory=list)


class VideoItem(BaseModel):
    """Normalized educational video item from YouTube Data API."""
    video_id: str = Field(default="", description="YouTube video ID")
    title: str = Field(default="", description="Video title")
    description: str = Field(default="", description="Video snippet description")
    channel_title: str = Field(default="", description="Creator or channel name")
    published_at: str = Field(default="", description="ISO publication timestamp")
    thumbnail: str = Field(default="", description="URL to video thumbnail image")
    video_url: str = Field(default="", description="Direct watch URL for the video")


class VideosResponse(BaseModel):
    """API response model for video search."""
    topic: str
    videos: List[VideoItem] = Field(default_factory=list)


class StudyPackResourcesResponse(BaseModel):
    """Combined supplementary educational resources."""
    topic: str
    books: List[BookItem] = Field(default_factory=list)
    videos: List[VideoItem] = Field(default_factory=list)
