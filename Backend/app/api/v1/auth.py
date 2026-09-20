"""OAuth Authentication endpoints for Google Drive and GitHub."""

import logging
from pathlib import Path
from typing import Optional
import urllib.parse
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx

from app.config import settings
from app.services.mcp_client import mcp_client

logger = logging.getLogger(__name__)

router = APIRouter()


def update_env_file(updates: dict):
    """Safely updates or appends key-value pairs in Backend/.env and root .env."""
    env_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / ".env",  # Backend/.env
        Path(__file__).resolve().parent.parent.parent.parent.parent / ".env",  # root .env
    ]
    for env_path in env_paths:
        if not env_path.exists():
            continue
        try:
            content = env_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            found_keys = set()
            new_lines = []
            for line in lines:
                stripped = line.strip()
                replaced = False
                for k, v in updates.items():
                    if stripped.startswith(f"{k}=") or stripped.startswith(f"export {k}="):
                        new_lines.append(f'{k}="{v}"')
                        found_keys.add(k)
                        replaced = True
                        break
                if not replaced:
                    new_lines.append(line)

            for k, v in updates.items():
                if k not in found_keys:
                    new_lines.append(f'{k}="{v}"')

            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            logger.info("Updated %s with keys: %s", env_path.name, list(updates.keys()))
        except Exception as exc:
            logger.error("Failed to update env file %s: %s", env_path, exc)


@router.get("/google/login")
async def google_login():
    """
    Redirects the user to Google OAuth 2.0 consent screen.
    Requests offline access and prompt=consent to ensure a refresh_token is returned.
    """
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URL

    if not client_id:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_CLIENT_ID is not configured in Backend/.env",
        )

    scopes = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "select_account consent",
        "include_granted_scopes": "true",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.post("/google/disconnect")
@router.delete("/google/disconnect")
async def google_disconnect():
    """
    Disconnects Google Drive by clearing cached and stored tokens.
    Allows user to switch to another Google account easily.
    """
    token_to_revoke = (
        mcp_client._cached_access_token
        or getattr(settings, "GOOGLE_DRIVE_MCP_TOKEN", "")
        or getattr(settings, "GOOGLE_REFRESH_TOKEN", "")
    )

    # 1. Attempt token revocation at Google (non-blocking if fails)
    if token_to_revoke:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": token_to_revoke},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            logger.info("Revoked Google OAuth token.")
        except Exception as exc:
            logger.warning("Could not revoke token at Google: %s", exc)

    # 2. Clear in-memory tokens
    mcp_client.clear_cached_token()
    settings.GOOGLE_DRIVE_MCP_TOKEN = ""
    settings.GOOGLE_REFRESH_TOKEN = ""

    # 3. Clear tokens in .env files
    update_env_file({
        "GOOGLE_DRIVE_MCP_TOKEN": "",
        "GOOGLE_REFRESH_TOKEN": "",
    })

    logger.info("Google Drive disconnected successfully.")
    return {"status": "disconnected", "message": "Google Drive disconnected successfully"}


@router.get("/google/callback")

async def google_callback(
    code: Optional[str] = Query(default=None),
    error: Optional[str] = Query(default=None),
):
    """
    Handles callback from Google OAuth, exchanges the authorization code for
    access_token and refresh_token, and saves them for automatic background refresh.
    """
    frontend_url = settings.FRONTEND_URL.rstrip("/")

    if error:
        logger.error("Google OAuth returned error: %s", error)
        return RedirectResponse(url=f"{frontend_url}/?google_auth_error={urllib.parse.quote(error)}")

    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received from Google")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URL,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if token_response.status_code != 200:
            logger.error("Google token exchange failed: %s", token_response.text)
            return RedirectResponse(
                url=f"{frontend_url}/?google_auth_error={urllib.parse.quote('Token exchange failed')}"
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = int(tokens.get("expires_in", 3600))

        env_updates = {}
        if access_token:
            env_updates["GOOGLE_DRIVE_MCP_TOKEN"] = access_token
            mcp_client.set_cached_token(access_token, expires_in)

        if refresh_token:
            env_updates["GOOGLE_REFRESH_TOKEN"] = refresh_token
            settings.GOOGLE_REFRESH_TOKEN = refresh_token

        if env_updates:
            update_env_file(env_updates)

        logger.info("Successfully connected Google Drive! Refresh token saved: %s", bool(refresh_token))
        return RedirectResponse(url=f"{frontend_url}/?google_drive_connected=true")

    except Exception as exc:
        logger.error("Unexpected error in Google OAuth callback: %s", exc, exc_info=True)
        return RedirectResponse(url=f"{frontend_url}/?google_auth_error={urllib.parse.quote(str(exc))}")
