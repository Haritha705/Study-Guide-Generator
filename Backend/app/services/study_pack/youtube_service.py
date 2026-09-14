"""YouTube Data API v3 integration for supplementary educational video resources."""

import html
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from langchain_core.tools import tool

from app.config import settings

logger = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_WATCH_BASE_URL = "https://www.youtube.com/watch?v="
DEFAULT_TIMEOUT_SECONDS = 8.0


def parse_youtube_video_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Safely extract and normalize video metadata from YouTube search response item.
    Constructs full watch URL and cleans HTML entities in titles and descriptions.
    """
    if not isinstance(item, dict):
        return None

    # Video ID extraction
    id_info = item.get("id")
    video_id = ""
    if isinstance(id_info, dict):
        video_id = str(id_info.get("videoId", "")).strip()
    elif isinstance(id_info, str):
        video_id = id_info.strip()

    if not video_id:
        return None

    snippet = item.get("snippet")
    if not isinstance(snippet, dict):
        return None

    # Clean HTML entities (e.g. &amp;, &#39;, &quot;)
    raw_title = str(snippet.get("title", "")).strip()
    title = html.unescape(raw_title) if raw_title else ""
    if not title:
        return None

    raw_description = str(snippet.get("description", "")).strip()
    description = html.unescape(raw_description) if raw_description else ""

    channel_title = html.unescape(str(snippet.get("channelTitle", "")).strip())
    published_at = str(snippet.get("publishedAt", "")).strip()

    # Thumbnail resolution priority: medium -> high -> default
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = ""
    if isinstance(thumbnails, dict):
        for quality in ("medium", "high", "standard", "default"):
            thumb_obj = thumbnails.get(quality)
            if isinstance(thumb_obj, dict) and thumb_obj.get("url"):
                thumbnail = str(thumb_obj["url"]).strip()
                break

    video_url = f"{YOUTUBE_WATCH_BASE_URL}{video_id}"

    return {
        "video_id": video_id,
        "title": title,
        "description": description,
        "channel_title": channel_title,
        "published_at": published_at,
        "thumbnail": thumbnail,
        "video_url": video_url,
    }


def search_educational_videos(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search YouTube Data API v3 for high-quality educational videos matching a topic.

    Parameters:
    - part=snippet
    - q=<topic>
    - type=video
    - maxResults=5
    - order=relevance
    - relevanceLanguage=en
    - videoCaption=closedCaption

    Gracefully handles:
    - missing / invalid API key
    - quota errors (HTTP 403 quotaExceeded)
    - timeouts
    - empty results
    - malformed responses
    """
    if not topic or not topic.strip():
        return []

    api_key = getattr(settings, "YOUTUBE_API_KEY", "").strip()
    if not api_key:
        logger.warning(
            "YOUTUBE_API_KEY is not set. YouTube search will return empty results. "
            "Please set YOUTUBE_API_KEY in Backend/.env."
        )
        return []

    clean_topic = topic.strip()
    safe_max_results = min(max(1, max_results), 5)

    base_params = {
        "part": "snippet",
        "q": clean_topic,
        "type": "video",
        "maxResults": safe_max_results,
        "order": "relevance",
        "relevanceLanguage": "en",
        "key": api_key,
    }

    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            # First attempt with closedCaption filter for educational rigor
            params_with_caption = {**base_params, "videoCaption": "closedCaption"}
            response = client.get(YOUTUBE_SEARCH_URL, params=params_with_caption)

            # Check status and quota
            if response.status_code == 403:
                error_body = response.text
                if "quotaExceeded" in error_body:
                    logger.warning("YouTube API quota exceeded. Returning empty video list.")
                else:
                    logger.warning("YouTube API authorization/forbidden error (403): %s", error_body[:200])
                return []

            if response.status_code == 400:
                logger.warning("YouTube API bad request (invalid key or parameter): %s", response.text[:200])
                return []

            if response.status_code != 200:
                logger.warning("YouTube API returned HTTP %d: %s", response.status_code, response.text[:200])
                return []

            payload = response.json()

            # If closedCaption yielded 0 items, fall back to standard relevance query without caption filter
            items = payload.get("items", []) if isinstance(payload, dict) else []
            if not items:
                response_fallback = client.get(YOUTUBE_SEARCH_URL, params=base_params)
                if response_fallback.status_code == 200:
                    fallback_payload = response_fallback.json()
                    if isinstance(fallback_payload, dict):
                        items = fallback_payload.get("items", [])

    except (httpx.TimeoutException, httpx.RequestError) as exc:
        logger.warning("YouTube API request timed out or network failed: %s", exc)
        return []
    except (ValueError, TypeError) as exc:
        logger.warning("Failed to decode YouTube API JSON payload: %s", exc)
        return []
    except Exception as exc:
        logger.error("Unexpected error querying YouTube Data API: %s", exc)
        return []

    if not isinstance(items, list) or not items:
        return []

    results: List[Dict[str, Any]] = []
    for item in items:
        parsed = parse_youtube_video_item(item)
        if parsed:
            results.append(parsed)
        if len(results) >= safe_max_results:
            break

    return results


@tool("search_youtube_videos")
def search_youtube_videos(topic: str) -> str:
    """
    Search YouTube for relevant educational videos and lectures on a topic.
    Returns a JSON string containing the list of videos with title, channel, and watch URL.
    """
    videos = search_educational_videos(topic=topic, max_results=5)
    return json.dumps({"topic": topic, "videos": videos}, ensure_ascii=False)
