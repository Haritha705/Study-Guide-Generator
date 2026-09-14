"""
Unit and integration tests for StudyPack external educational resources
(Google Books API & YouTube Data API).

All HTTP interactions are mocked; no live network calls are made.
"""

import json
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings
from app.services.study_pack.books_service import search_books, search_books_tool
from app.services.study_pack.youtube_service import search_educational_videos, search_youtube_videos
from app.services.study_pack.resource_service import get_study_resources


# =====================================================================
# Fixtures & Sample Mock Payloads
# =====================================================================

MOCK_GOOGLE_BOOKS_PAYLOAD = {
    "kind": "books#volumes",
    "totalItems": 1,
    "items": [
        {
            "id": "book123",
            "volumeInfo": {
                "title": "Deep Learning Fundamentals",
                "authors": ["Ian Goodfellow", "Yoshua Bengio"],
                "publisher": "MIT Press",
                "publishedDate": "2016-11-18",
                "description": "An introduction to a broad range of topics in deep learning.",
                "imageLinks": {
                    "smallThumbnail": "http://books.google.com/thumbnail.jpg",
                    "thumbnail": "http://books.google.com/thumbnail.jpg",
                },
                "previewLink": "https://books.google.com/preview/book123",
                "infoLink": "https://books.google.com/info/book123",
                "categories": ["Computers / Intelligence (AI)"],
            },
        }
    ],
}

MOCK_YOUTUBE_PAYLOAD = {
    "kind": "youtube#searchListResponse",
    "items": [
        {
            "id": {
                "kind": "youtube#video",
                "videoId": "dQw4w9WgXcQ",
            },
            "snippet": {
                "publishedAt": "2023-01-15T10:00:00Z",
                "channelId": "UC12345",
                "title": "Machine Learning for Beginners &amp; Experts",
                "description": "Comprehensive tutorial covering neural networks &amp; algorithms.",
                "channelTitle": "3Blue1Brown",
                "thumbnails": {
                    "medium": {
                        "url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
                        "width": 320,
                        "height": 180,
                    }
                },
            },
        }
    ],
}


# =====================================================================
# 1. Google Books Tests
# =====================================================================

def test_google_books_successful_response():
    """Test 1: Google Books successfully parses all volume metadata fields."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_GOOGLE_BOOKS_PAYLOAD

    with patch("httpx.Client.get", return_value=mock_resp):
        books = search_books(query="machine learning", max_results=5)

    assert len(books) == 1
    book = books[0]
    assert book["title"] == "Deep Learning Fundamentals"
    assert book["authors"] == ["Ian Goodfellow", "Yoshua Bengio"]
    assert book["publisher"] == "MIT Press"
    assert book["publishedDate"] == "2016-11-18"
    assert "deep learning" in book["description"].lower()
    assert book["thumbnail"].startswith("https://")  # Normalized to https
    assert book["previewLink"] == "https://books.google.com/preview/book123"
    assert book["infoLink"] == "https://books.google.com/info/book123"
    assert book["categories"] == ["Computers / Intelligence (AI)"]


def test_google_books_empty_response():
    """Test 2: Google Books gracefully handles empty items or zero results."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"totalItems": 0, "items": []}

    with patch("httpx.Client.get", return_value=mock_resp):
        books = search_books(query="nonexistenttopicxyz123")
    assert books == []

    # Also test empty query string directly
    assert search_books(query="") == []
    assert search_books(query="   ") == []


def test_google_books_api_error_and_timeout():
    """Test 3: Google Books handles HTTP errors, timeouts, and malformed JSON."""
    # 3a. HTTP 500
    mock_500 = MagicMock()
    mock_500.status_code = 500
    mock_500.text = "Internal Server Error"
    with patch("httpx.Client.get", return_value=mock_500):
        assert search_books(query="machine learning") == []

    # 3b. Request Timeout
    with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timeout")):
        assert search_books(query="machine learning") == []

    # 3c. Malformed JSON
    mock_malformed = MagicMock()
    mock_malformed.status_code = 200
    mock_malformed.json.side_effect = ValueError("Invalid JSON")
    with patch("httpx.Client.get", return_value=mock_malformed):
        assert search_books(query="machine learning") == []


# =====================================================================
# 2. YouTube Data API Tests
# =====================================================================

def test_youtube_successful_response():
    """Test 4: YouTube Data API parses snippets, cleans HTML entities, and builds watch URLs."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_YOUTUBE_PAYLOAD

    with patch.object(settings, "YOUTUBE_API_KEY", "test-youtube-key"):
        with patch("httpx.Client.get", return_value=mock_resp):
            videos = search_educational_videos(topic="machine learning", max_results=5)

    assert len(videos) == 1
    video = videos[0]
    assert video["video_id"] == "dQw4w9WgXcQ"
    # Verifies HTML entities unescaped
    assert video["title"] == "Machine Learning for Beginners & Experts"
    assert "neural networks & algorithms" in video["description"]
    assert video["channel_title"] == "3Blue1Brown"
    assert video["published_at"] == "2023-01-15T10:00:00Z"
    assert video["thumbnail"] == "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
    assert video["video_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_youtube_quota_and_api_error():
    """Test 5: YouTube gracefully handles quota exhaustion, missing keys, and HTTP errors."""
    # 5a. Quota Exceeded (HTTP 403)
    mock_quota = MagicMock()
    mock_quota.status_code = 403
    mock_quota.text = '{"error": {"errors": [{"reason": "quotaExceeded"}]}}'

    with patch.object(settings, "YOUTUBE_API_KEY", "test-youtube-key"):
        with patch("httpx.Client.get", return_value=mock_quota):
            videos = search_educational_videos(topic="machine learning")
            assert videos == []

    # 5b. Missing API Key
    with patch.object(settings, "YOUTUBE_API_KEY", ""):
        assert search_educational_videos(topic="machine learning") == []

    # 5c. Bad Request (HTTP 400)
    mock_400 = MagicMock()
    mock_400.status_code = 400
    mock_400.text = "API key not valid"
    with patch.object(settings, "YOUTUBE_API_KEY", "invalid-key"):
        with patch("httpx.Client.get", return_value=mock_400):
            assert search_educational_videos(topic="machine learning") == []

    # 5d. Timeout
    with patch.object(settings, "YOUTUBE_API_KEY", "test-key"):
        with patch("httpx.Client.get", side_effect=httpx.TimeoutException("Timeout")):
            assert search_educational_videos(topic="machine learning") == []


def test_youtube_empty_response():
    """Test 6: YouTube gracefully handles empty items and fallback queries."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"items": []}

    with patch.object(settings, "YOUTUBE_API_KEY", "test-youtube-key"):
        with patch("httpx.Client.get", return_value=mock_resp):
            videos = search_educational_videos(topic="extremelyobscuretopic12345")
            assert videos == []

    # Empty topic string
    assert search_educational_videos(topic="") == []
    assert search_educational_videos(topic="   ") == []


# =====================================================================
# 3. Resource Aggregator Service Tests
# =====================================================================

def test_resource_service_combining_both():
    """Test 7: Central resource service aggregates books and videos, with failure isolation."""
    sample_book = {
        "title": "Test Book",
        "authors": ["Author"],
        "publisher": "Pub",
        "publishedDate": "2022",
        "description": "Desc",
        "thumbnail": "",
        "previewLink": "",
        "infoLink": "",
        "categories": [],
    }
    sample_video = {
        "video_id": "vid123",
        "title": "Test Video",
        "description": "Desc",
        "channel_title": "Channel",
        "published_at": "2023",
        "thumbnail": "",
        "video_url": "https://www.youtube.com/watch?v=vid123",
    }

    # 7a. Successful combination of both
    with patch("app.services.study_pack.resource_service.search_books", return_value=[sample_book]):
        with patch("app.services.study_pack.resource_service.search_educational_videos", return_value=[sample_video]):
            result = get_study_resources(topic="Quantum Computing")
            assert result["topic"] == "Quantum Computing"
            assert len(result["books"]) == 1
            assert len(result["videos"]) == 1
            assert result["books"][0]["title"] == "Test Book"
            assert result["videos"][0]["video_id"] == "vid123"

    # 7b. Partial failure isolation: YouTube throws error, books still returned
    with patch("app.services.study_pack.resource_service.search_books", return_value=[sample_book]):
        with patch("app.services.study_pack.resource_service.search_educational_videos", side_effect=Exception("API Error")):
            result = get_study_resources(topic="Quantum Computing")
            assert len(result["books"]) == 1
            assert result["videos"] == []


# =====================================================================
# 4. FastAPI Endpoint Tests
# =====================================================================

def test_api_endpoints_books_and_videos():
    """Test 8: FastAPI endpoints return validated response schemas."""
    client = TestClient(app)

    # 8a. GET /study-pack/books
    sample_book = {
        "title": "Machine Learning Yearning",
        "authors": ["Andrew Ng"],
        "publisher": "Deeplearning.ai",
        "publishedDate": "2018",
        "description": "Technical strategy guide.",
        "thumbnail": "https://example.com/thumb.jpg",
        "previewLink": "https://example.com/preview",
        "infoLink": "https://example.com/info",
        "categories": ["AI"],
    }
    with patch("app.api.v1.study_pack.search_books", return_value=[sample_book]):
        resp = client.get("/study-pack/books?topic=machine learning")
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "machine learning"
        assert len(data["books"]) == 1
        assert data["books"][0]["title"] == "Machine Learning Yearning"

        # Also verify prefix /api/v1/study-pack/books
        resp_v1 = client.get("/api/v1/study-pack/books?topic=machine learning")
        assert resp_v1.status_code == 200
        assert len(resp_v1.json()["books"]) == 1

    # 8b. GET /study-pack/videos
    sample_video = {
        "video_id": "ml_101",
        "title": "Machine Learning in 100 Seconds",
        "description": "Quick overview of ML concepts.",
        "channel_title": "Fireship",
        "published_at": "2021-05-12T00:00:00Z",
        "thumbnail": "https://i.ytimg.com/vi/ml_101/mqdefault.jpg",
        "video_url": "https://www.youtube.com/watch?v=ml_101",
    }
    with patch("app.api.v1.study_pack.search_educational_videos", return_value=[sample_video]):
        resp = client.get("/study-pack/videos?topic=machine learning")
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "machine learning"
        assert len(data["videos"]) == 1
        assert data["videos"][0]["video_id"] == "ml_101"

        # Also verify prefix /api/v1/study-pack/videos
        resp_v1 = client.get("/api/v1/study-pack/videos?topic=machine learning")
        assert resp_v1.status_code == 200
        assert len(resp_v1.json()["videos"]) == 1

    # 8c. GET /study-pack/resources
    with patch("app.api.v1.study_pack.get_study_resources", return_value={"topic": "ML", "books": [sample_book], "videos": [sample_video]}):
        resp = client.get("/study-pack/resources?topic=ML")
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "ML"
        assert len(data["books"]) == 1
        assert len(data["videos"]) == 1

    # 8d. Missing topic parameter returns 422 Unprocessable Entity
    resp_missing = client.get("/study-pack/books")
    assert resp_missing.status_code == 422


# =====================================================================
# 5. LangChain Tool Execution Tests
# =====================================================================

def test_langchain_tools_execution():
    """Verify search_books_tool and search_youtube_videos LangChain tools invoke properly."""
    sample_book = {"title": "Calculus", "authors": ["Stewart"], "publisher": "Cengage", "publishedDate": "2015", "description": "Math", "thumbnail": "", "previewLink": "", "infoLink": "", "categories": []}
    sample_video = {"video_id": "calc1", "title": "Essence of Calculus", "description": "Visual intro", "channel_title": "3Blue1Brown", "published_at": "2017", "thumbnail": "", "video_url": "https://www.youtube.com/watch?v=calc1"}

    with patch("app.services.study_pack.books_service.search_books", return_value=[sample_book]):
        tool_output = search_books_tool.invoke({"topic": "calculus"})
        parsed = json.loads(tool_output)
        assert parsed["topic"] == "calculus"
        assert len(parsed["books"]) == 1
        assert parsed["books"][0]["title"] == "Calculus"

    with patch("app.services.study_pack.youtube_service.search_educational_videos", return_value=[sample_video]):
        tool_output = search_youtube_videos.invoke({"topic": "calculus"})
        parsed = json.loads(tool_output)
        assert parsed["topic"] == "calculus"
        assert len(parsed["videos"]) == 1
        assert parsed["videos"][0]["video_id"] == "calc1"
