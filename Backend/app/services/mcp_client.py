"""External Document MCP Client for StudyPack AI.

Integrates with Model Context Protocol (MCP) servers, specifically Google's official
Google Drive MCP endpoint (https://drivemcp.googleapis.com/mcp/v1).
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MCP_URL = "https://drivemcp.googleapis.com/mcp/v1"
DEFAULT_TIMEOUT_SECONDS = 15.0


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    def __init__(self, message: str, status_code: int = 502, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class MCPAuthenticationError(MCPClientError):
    """Exception raised when MCP server requires authentication credentials."""
    def __init__(self, message: str = "Google Drive OAuth token required.", details: Any = None):
        super().__init__(message=message, status_code=401, details=details)


class ExternalDocumentMCPClient:
    """
    Client for Model Context Protocol (MCP) servers.
    Supports official Google Drive MCP server (https://drivemcp.googleapis.com/mcp/v1)
    and JSON-RPC 2.0 tool execution.
    """

    def __init__(self, mcp_server_url: Optional[str] = None):
        self.mcp_server_url = (
            mcp_server_url
            or getattr(settings, "GOOGLE_DRIVE_MCP_URL", None)
            or os.getenv("GOOGLE_DRIVE_MCP_URL")
            or os.getenv("MCP_SERVER_URL")
            or DEFAULT_MCP_URL
        )
        self._req_id = 0

    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    # Path where the Antigravity IDE stores MCP OAuth tokens
    _IDE_TOKEN_FILE = Path.home() / ".gemini" / "antigravity-ide" / "mcp_oauth_tokens.json"
    _MCP_SERVER_KEY = "https://drivemcp.googleapis.com/mcp/v1"

    # Token caching attributes
    _cached_access_token: Optional[str] = None
    _token_expires_at: float = 0.0

    def set_cached_token(self, token: str, expires_in: int = 3600) -> None:
        """Cache an access token with an expiration buffer."""
        import time
        self._cached_access_token = token
        self._token_expires_at = time.time() + max(expires_in - 120, 60)
        logger.info("Cached fresh Google OAuth access token (expires in %ss)", expires_in)

    def clear_cached_token(self) -> None:
        """Clear cached access token and expiration."""
        self._cached_access_token = None
        self._token_expires_at = 0.0
        logger.info("Cleared cached Google Drive access token.")

    async def refresh_access_token(self) -> Optional[str]:
        """
        Exchange GOOGLE_REFRESH_TOKEN with Google OAuth endpoint for a fresh access token.
        """
        import time
        refresh_token = (
            getattr(settings, "GOOGLE_REFRESH_TOKEN", "")
            or os.getenv("GOOGLE_REFRESH_TOKEN", "")
        ).strip()
        client_id = (
            getattr(settings, "GOOGLE_CLIENT_ID", "")
            or os.getenv("GOOGLE_CLIENT_ID", "")
        ).strip()
        client_secret = (
            getattr(settings, "GOOGLE_CLIENT_SECRET", "")
            or os.getenv("GOOGLE_CLIENT_SECRET", "")
        ).strip()

        if not (refresh_token and client_id and client_secret):
            return None

        try:
            logger.info("Attempting automatic refresh of Google Drive OAuth access token...")
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

            if res.status_code == 200:
                data = res.json()
                new_token = data.get("access_token", "").strip()
                expires_in = int(data.get("expires_in", 3600))
                if new_token:
                    self._cached_access_token = new_token
                    self._token_expires_at = time.time() + max(expires_in - 120, 60)
                    logger.info("Successfully refreshed Google Drive OAuth token (expires in %ss)", expires_in)
                    return new_token
            else:
                logger.warning(
                    "Failed to refresh Google OAuth token: HTTP %s - %s",
                    res.status_code,
                    res.text[:200],
                )
                return None
        except Exception as exc:
            logger.error("Error refreshing Google OAuth token: %s", exc)
            return None

    def _read_token_from_ide_file(self) -> str:
        """
        Read the current OAuth access token from the Antigravity IDE token store.
        Falls back gracefully if the file doesn't exist or can't be read.
        Returns empty string on any failure.
        """
        try:
            if not self._IDE_TOKEN_FILE.exists():
                return ""
            raw = self._IDE_TOKEN_FILE.read_text(encoding="utf-8")
            data = json.loads(raw)
            entry = data.get(self._MCP_SERVER_KEY, {})
            token_obj = entry.get("token", {})
            access_token = token_obj.get("access_token", "")
            if not access_token:
                return ""

            # Check expiry — skip if expired (with 30-second buffer)
            expiry_str = token_obj.get("expiry", "")
            if expiry_str:
                from datetime import datetime, timezone
                try:
                    expiry = datetime.fromisoformat(expiry_str)
                    if expiry.tzinfo is None:
                        expiry = expiry.replace(tzinfo=timezone.utc)
                    now = datetime.now(tz=timezone.utc)
                    if expiry <= now:
                        logger.info("IDE OAuth token is expired (expiry=%s), skipping.", expiry_str)
                        return ""
                except ValueError:
                    pass

            return access_token.strip()
        except Exception as exc:
            logger.debug("Could not read IDE OAuth token file: %s", exc)
            return ""

    async def get_valid_token(self, token: Optional[str] = None, force_refresh: bool = False) -> str:
        """
        Resolves a valid Google Drive OAuth token with automatic refreshing.
        Priority:
        1. Explicitly-passed per-request token.
        2. Cached access token (if not expired and not force_refresh).
        3. Auto-refreshed access token via GOOGLE_REFRESH_TOKEN.
        4. Environment/Settings GOOGLE_DRIVE_MCP_TOKEN.
        5. IDE token store fallback.
        """
        if token and token.strip():
            return token.strip()

        import time
        if self._cached_access_token and time.time() < self._token_expires_at and not force_refresh:
            return self._cached_access_token

        # Attempt auto-refresh if refresh credentials are present
        refreshed = await self.refresh_access_token()
        if refreshed:
            return refreshed

        # Fallback to configured environment token
        env_token = (
            getattr(settings, "GOOGLE_DRIVE_MCP_TOKEN", "")
            or os.getenv("GOOGLE_DRIVE_MCP_TOKEN", "")
        ).strip()
        if env_token:
            return env_token

        # Fallback to IDE token file
        ide_token = self._read_token_from_ide_file()
        if ide_token:
            return ide_token

        return ""

    def _resolve_token(self, token: Optional[str] = None) -> str:
        """Synchronous token resolver (returns cached or env token)."""
        if token and token.strip():
            return token.strip()
        if self._cached_access_token:
            return self._cached_access_token
        env_token = (
            getattr(settings, "GOOGLE_DRIVE_MCP_TOKEN", "")
            or os.getenv("GOOGLE_DRIVE_MCP_TOKEN", "")
        ).strip()
        if env_token:
            return env_token
        return self._read_token_from_ide_file()

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        resolved = token or self._resolve_token()
        if resolved:
            headers["Authorization"] = f"Bearer {resolved}"
        return headers

    async def connect(self) -> Dict[str, Any]:
        """
        Verify connection to Google Drive by:
        1. Checking/refreshing the OAuth token.
        2. Testing access against Google Drive API (and Drive MCP endpoint).
        """
        token = await self.get_valid_token()

        if not token:
            return {
                "connected": False,
                "server_url": self.mcp_server_url,
                "status": "HTTP 401",
                "detail": (
                    "Google Drive OAuth token not found. "
                    "Please connect your Google Drive account or configure "
                    "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN."
                ),
            }

        drive_tools = [
            "list_recent_files",
            "search_files",
            "download_file_content",
            "read_file_content",
        ]

        # 1. Verify against Google Drive REST API (and auto-refresh on 401)
        async def _test_drive_api(tok: str):
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
                return await client.get(
                    "https://www.googleapis.com/drive/v3/about?fields=user",
                    headers={"Authorization": f"Bearer {tok}"},
                )

        try:
            r = await _test_drive_api(token)
            if r.status_code in (401, 403):
                # Try force refreshing the token
                new_tok = await self.get_valid_token(force_refresh=True)
                if new_tok and new_tok != token:
                    token = new_tok
                    r = await _test_drive_api(token)

            if r.status_code == 200:
                user_data = r.json().get("user", {})
                display_name = user_data.get("displayName", "")
                email = user_data.get("emailAddress", "")
                detail = f"Connected as {display_name} ({email})" if email else "Google Drive connected successfully"
                return {
                    "connected": True,
                    "server_url": self.mcp_server_url,
                    "status": "ready",
                    "tools_count": len(drive_tools),
                    "tools": drive_tools,
                    "detail": detail,
                }
            elif r.status_code in (401, 403):
                return {
                    "connected": False,
                    "server_url": self.mcp_server_url,
                    "status": f"HTTP {r.status_code}",
                    "detail": (
                        "Google Drive authentication failed. "
                        "The token is expired or invalid. Please reconnect Google Drive."
                    ),
                }
        except Exception as exc:
            logger.debug("Direct Drive API ping encountered: %s", exc)

        # 2. Fallback to MCP tools/list endpoint
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
        }
        headers = self._get_headers(token=token)

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    self.mcp_server_url,
                    json=payload,
                    headers=headers,
                )

            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    return {
                        "connected": False,
                        "server_url": self.mcp_server_url,
                        "status": "MCP error",
                        "detail": data["error"].get("message", "Unknown MCP server error"),
                    }
                tools = data.get("result", {}).get("tools", [])
                tool_names = [t.get("name") for t in tools if isinstance(t, dict) and t.get("name")]
                return {
                    "connected": True,
                    "server_url": self.mcp_server_url,
                    "status": "ready",
                    "tools_count": len(tool_names),
                    "tools": tool_names,
                }

            return {
                "connected": False,
                "server_url": self.mcp_server_url,
                "status": f"HTTP {response.status_code}",
                "detail": response.text[:300],
            }
        except Exception as exc:
            return {
                "connected": False,
                "server_url": self.mcp_server_url,
                "status": "error",
                "detail": str(exc),
            }

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool via JSON-RPC 2.0 tools/call.
        Automatically resolves fresh token and includes fallback to Drive REST API.
        """
        resolved_token = await self.get_valid_token(token)
        if not resolved_token:
            raise MCPAuthenticationError(
                "Google Drive OAuth access token is required. "
                "Please connect Google Drive or configure GOOGLE_REFRESH_TOKEN."
            )

        # LOCAL FALLBACK FOR GOOGLE DRIVE API
        if "drive" in self.mcp_server_url.lower():
            try:
                return await self._execute_drive_tool_local(tool_name, arguments, resolved_token)
            except MCPAuthenticationError:
                # Try force refreshing token once
                new_token = await self.get_valid_token(force_refresh=True)
                if new_token and new_token != resolved_token:
                    return await self._execute_drive_tool_local(tool_name, arguments, new_token)
                raise
            except Exception as e:
                logger.warning(f"Local Drive tool execution failed, falling back to MCP server: {e}")
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        headers = self._get_headers(token=resolved_token)

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    self.mcp_server_url,
                    json=payload,
                    headers=headers,
                )

            if response.status_code in (401, 403):
                raise MCPAuthenticationError(
                    f"Authentication failed with Google Drive MCP server: {response.text[:200]}"
                )

            if response.status_code != 200:
                raise MCPClientError(
                    f"Google Drive MCP server returned HTTP {response.status_code}: {response.text[:200]}",
                    status_code=response.status_code,
                )

            data = response.json()

            if "error" in data:
                err = data["error"]
                msg = err.get("message", "Unknown MCP JSON-RPC error")
                code = err.get("code", 500)
                if code in (401, -32000) and "auth" in msg.lower():
                    raise MCPAuthenticationError(msg)
                raise MCPClientError(f"MCP tool error: {msg}", status_code=502, details=err)

            result = data.get("result", {})
            if result.get("isError"):
                content = result.get("content", [])
                err_text = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict)
                ) or "Tool execution reported error"
                if "authentication credential" in err_text.lower() or "oauth" in err_text.lower():
                    raise MCPAuthenticationError(err_text)
                raise MCPClientError(err_text, status_code=502, details=result)

            return result

        except (MCPClientError, MCPAuthenticationError):
            raise
        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.error("Network error calling MCP tool %s: %s", tool_name, exc)
            raise MCPClientError(f"Failed to communicate with Google Drive MCP: {exc}")
        except Exception as exc:
            logger.error("Unexpected error calling MCP tool %s: %s", tool_name, exc)
            raise MCPClientError(f"Unexpected error executing MCP tool: {exc}")

    async def _execute_drive_tool_local(self, tool_name: str, arguments: Dict[str, Any], token: str) -> Dict[str, Any]:
        """Executes Drive MCP tools directly against the Google Drive REST API."""
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            if tool_name in ("list_recent_files", "search_files"):
                page_size = arguments.get("pageSize", 10)
                query = arguments.get("query", "")
                
                params = {
                    "pageSize": page_size,
                    "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
                    "orderBy": "modifiedTime desc"
                }
                
                # If it's a specific search query (like type:pdf), map it to Drive query syntax
                q_parts = []
                if "pdf" in query.lower():
                    q_parts.append("mimeType='application/pdf'")
                if query and "pdf" not in query.lower():
                    q_parts.append(f"name contains '{query}'")
                    
                if q_parts:
                    params["q"] = " and ".join(q_parts)
                elif tool_name == "list_recent_files":
                    # For recent files, only fetch PDFs by default to keep it clean
                    params["q"] = "mimeType='application/pdf'"

                r = await client.get("https://www.googleapis.com/drive/v3/files", params=params, headers=headers)
                if r.status_code in (401, 403):
                    raise MCPAuthenticationError("Drive API token invalid or expired.")
                r.raise_for_status()
                
                return {
                    "content": [{"type": "text", "text": json.dumps(r.json())}],
                    "isError": False
                }
                
            elif tool_name == "download_file_content":
                file_id = arguments.get("fileId")
                if not file_id:
                    raise ValueError("fileId required")
                
                r = await client.get(f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media", headers=headers)
                if r.status_code in (401, 403):
                    raise MCPAuthenticationError("Drive API token invalid or expired.")
                r.raise_for_status()
                
                # Encode binary as base64 to match MCP format
                encoded = base64.b64encode(r.content).decode('utf-8')
                return {
                    "content": [{"type": "text", "text": encoded}],
                    "isError": False
                }
                
            elif tool_name == "read_file_content":
                # Fallback to downloading bytes
                return await self._execute_drive_tool_local("download_file_content", arguments, token)
                
            else:
                raise NotImplementedError(f"Local execution for {tool_name} not implemented")

    async def search_files(
        self,
        query: str = "",
        page_size: int = 10,
        token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search or list files in user's Google Drive via MCP.
        """
        clean_query = query.strip() if query else ""
        safe_size = min(max(1, page_size), 50)

        if clean_query:
            result = await self.call_tool(
                "search_files",
                {"query": clean_query, "pageSize": safe_size},
                token=token,
            )
        else:
            result = await self.call_tool(
                "list_recent_files",
                {"pageSize": safe_size},
                token=token,
            )

        # Parse files from content
        content = result.get("content", [])
        files: List[Dict[str, Any]] = []

        for item in content:
            if not isinstance(item, dict):
                continue
            text = item.get("text", "")
            if not text:
                continue
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    files.extend(parsed)
                elif isinstance(parsed, dict):
                    if "files" in parsed and isinstance(parsed["files"], list):
                        files.extend(parsed["files"])
                    else:
                        files.append(parsed)
            except json.JSONDecodeError:
                files.append({"raw_snippet": text})

        return files

    async def download_file_bytes(
        self,
        file_id: str,
        token: Optional[str] = None,
    ) -> bytes:
        """
        Download raw binary content of a file from Google Drive via MCP.
        """
        if not file_id or not file_id.strip():
            raise MCPClientError("file_id is required", status_code=400)

        result = await self.call_tool(
            "download_file_content",
            {"fileId": file_id.strip()},
            token=token,
        )

        content = result.get("content", [])
        if not content:
            raise MCPClientError("No content returned for file", status_code=404)

        raw_payload = content[0].get("text", "")
        if not raw_payload:
            blob = content[0].get("data")
            if blob:
                raw_payload = blob

        if not raw_payload:
            raise MCPClientError("Empty file content received from Drive", status_code=404)

        try:
            return base64.b64decode(raw_payload)
        except Exception:
            # If not base64 encoded, return as utf-8 bytes
            return raw_payload.encode("utf-8")

    async def read_document_text(
        self,
        file_id: str,
        token: Optional[str] = None,
    ) -> str:
        """
        Fetch and parse document text from Google Drive.
        If PDF, parses pages via pypdf; otherwise reads text content.
        """
        from app.services.pdf_parser import parse_pdf

        try:
            # First attempt binary download and PDF extraction
            file_bytes = await self.download_file_bytes(file_id=file_id, token=token)
            if file_bytes.startswith(b"%PDF"):
                return parse_pdf(file_bytes)
            # Try parsing as PDF anyway
            try:
                return parse_pdf(file_bytes)
            except Exception:
                return file_bytes.decode("utf-8", errors="replace")
        except MCPClientError:
            # Fallback to read_file_content tool
            result = await self.call_tool(
                "read_file_content",
                {"fileId": file_id.strip()},
                token=token,
            )
            content = result.get("content", [])
            text_parts = [c.get("text", "") for c in content if isinstance(c, dict)]
            text = "\n".join(text_parts).strip()
            if not text:
                raise MCPClientError("No readable text found in document", status_code=400)
            return text

    async def fetch_document(self, resource_uri: str, token: Optional[str] = None) -> str:
        """
        Preserves backward compatibility for fetching documents by URI or file ID.
        """
        logger.info(f"Requesting resource: {resource_uri}")
        clean_id = resource_uri.replace("drive://", "").replace("gdrive://", "").strip()
        if not clean_id:
            return "Empty resource URI"
        return await self.read_document_text(file_id=clean_id, token=token)


mcp_client = ExternalDocumentMCPClient()
