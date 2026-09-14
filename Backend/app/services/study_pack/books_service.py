"""Google Books API integration for supplementary educational reading materials."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from langchain_core.tools import tool

from app.config import settings

logger = logging.getLogger(__name__)

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
DEFAULT_TIMEOUT_SECONDS = 8.0


def _clean_thumbnail_url(thumbnail: Optional[str]) -> str:
    """Normalize thumbnail URL, ensuring https protocol."""
    if not thumbnail:
        return ""
    if thumbnail.startswith("http://"):
        return thumbnail.replace("http://", "https://", 1)
    return thumbnail


def parse_volume_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely extract and normalize relevant volume metadata from Google Books item.
    Never invents metadata or placeholder books.
    """
    if not isinstance(item, dict):
        return None

    volume_info = item.get("volumeInfo")
    if not isinstance(volume_info, dict):
        return None

    title = str(volume_info.get("title", "")).strip()
    if not title:
        return None

    # Authors list
    authors_raw = volume_info.get("authors")
    if isinstance(authors_raw, list):
        authors = [str(a).strip() for a in authors_raw if str(a).strip()]
    elif isinstance(authors_raw, str) and authors_raw.strip():
        authors = [authors_raw.strip()]
    else:
        authors = []

    # Publisher & dates
    publisher = str(volume_info.get("publisher", "")).strip()
    published_date = str(volume_info.get("publishedDate", "")).strip()
    description = str(volume_info.get("description", "")).strip()

    # Image links / thumbnail
    image_links = volume_info.get("imageLinks")
    thumbnail = ""
    if isinstance(image_links, dict):
        raw_thumb = image_links.get("thumbnail") or image_links.get("smallThumbnail")
        if raw_thumb and isinstance(raw_thumb, str):
            thumbnail = _clean_thumbnail_url(raw_thumb)

    # Links
    preview_link = str(volume_info.get("previewLink", "")).strip()
    info_link = str(volume_info.get("infoLink", "")).strip()

    # Categories
    categories_raw = volume_info.get("categories")
    if isinstance(categories_raw, list):
        categories = [str(c).strip() for c in categories_raw if str(c).strip()]
    elif isinstance(categories_raw, str) and categories_raw.strip():
        categories = [categories_raw.strip()]
    else:
        categories = []

    return {
        "title": title,
        "authors": authors,
        "publisher": publisher,
        "publishedDate": published_date,
        "description": description,
        "thumbnail": thumbnail,
        "previewLink": preview_link,
        "infoLink": info_link,
        "categories": categories,
    }


def search_books(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Google Books Volumes API for the given query.

    Handles:
    - empty queries / no results
    - timeouts
    - HTTP/API errors
    - malformed responses
    Never invents books or metadata.
    """
    if not query or not query.strip():
        return []

    clean_query = query.strip()
    safe_max_results = min(max(1, max_results), 5)

    params: Dict[str, Any] = {
        "q": clean_query,
        "maxResults": safe_max_results,
        "printType": "books",
        "orderBy": "relevance",
    }

    # If an API key is configured, include it to increase quotas
    api_key = getattr(settings, "GOOGLE_BOOKS_API_KEY", "") or getattr(settings, "GEMINI_API_KEY", "")
    if getattr(settings, "GOOGLE_BOOKS_API_KEY", ""):
        params["key"] = settings.GOOGLE_BOOKS_API_KEY

    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            response = client.get(GOOGLE_BOOKS_API_URL, params=params)

        if response.status_code != 200:
            logger.warning(
                "Google Books API returned non-200 status: %d - %s",
                response.status_code,
                response.text[:200],
            )
            return []

        payload = response.json()
    except (httpx.TimeoutException, httpx.RequestError) as exc:
        logger.warning("Google Books request timed out or failed: %s", exc)
        return []
    except (ValueError, TypeError) as exc:
        logger.warning("Failed to parse Google Books response payload: %s", exc)
        return []
    except Exception as exc:
        logger.error("Unexpected error during Google Books search: %s", exc)
        return []

    if not isinstance(payload, dict):
        return []

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        return []

    results: List[Dict[str, Any]] = []
    for item in items:
        parsed = parse_volume_item(item)
        if parsed:
            results.append(parsed)
        if len(results) >= safe_max_results:
            break

    return results


@tool("search_books_tool")
def search_books_tool(topic: str) -> str:
    """
    Search Google Books for relevant educational books and supplementary reading material on a topic.
    Returns a JSON string containing the list of discovered books with metadata.
    """
    books = search_books(query=topic, max_results=5)
    return json.dumps({"topic": topic, "books": books}, ensure_ascii=False)
