"""API endpoints for Google Drive MCP integration."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Header, HTTPException, Query
from pydantic import BaseModel, Field

from app.schemas.studypack import StudyPackOutput
from app.services.ai_pipeline import generate_study_pack
from app.services.mcp_client import (
    mcp_client,
    MCPAuthenticationError,
    MCPClientError,
)
from app.core.exceptions import AIGenerationError

logger = logging.getLogger(__name__)

router = APIRouter()


class DriveGenerateRequest(BaseModel):
    file_id: str = Field(..., description="Google Drive file ID of the lecture/material PDF")
    token: Optional[str] = Field(default=None, description="Optional per-request Google OAuth access token")


class DriveExtractResponse(BaseModel):
    file_id: str
    extracted_text: str


class DriveFilesResponse(BaseModel):
    files: List[Dict[str, Any]] = Field(default_factory=list)
    count: int = 0


class DriveStatusResponse(BaseModel):
    connected: bool
    server_url: str
    status: str
    tools_count: Optional[int] = 0
    tools: Optional[List[str]] = Field(default_factory=list)
    detail: Optional[str] = None


@router.get("/status", response_model=DriveStatusResponse)
async def get_mcp_status():
    """
    Check connection status with the official Google Drive MCP server
    (https://drivemcp.googleapis.com/mcp/v1) and inspect available tools.
    """
    status_info = await mcp_client.connect()
    return DriveStatusResponse(**status_info)


@router.get("/files", response_model=DriveFilesResponse)
async def list_drive_files(
    query: str = Query(default="", description="Search query for Drive files (leave empty for recent)"),
    page_size: int = Query(default=10, ge=1, le=50, description="Max files to retrieve"),
    x_drive_token: Optional[str] = Header(default=None, alias="X-Drive-Token"),
):
    """
    Search and list Google Drive files through the Google Drive MCP server.
    """
    try:
        files = await mcp_client.search_files(
            query=query,
            page_size=page_size,
            token=x_drive_token,
        )
        return DriveFilesResponse(files=files, count=len(files))
    except MCPAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=exc.message)
    except MCPClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as exc:
        logger.error("Unexpected error searching Drive files: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error querying Google Drive via MCP")


@router.get("/files/{file_id}/extract", response_model=DriveExtractResponse)
async def extract_drive_pdf(
    file_id: str,
    x_drive_token: Optional[str] = Header(default=None, alias="X-Drive-Token"),
):
    """
    Download and parse text from a Google Drive PDF file via MCP.
    """
    if not file_id.strip():
        raise HTTPException(status_code=400, detail="file_id cannot be empty")

    try:
        text = await mcp_client.read_document_text(file_id=file_id.strip(), token=x_drive_token)
        return DriveExtractResponse(file_id=file_id.strip(), extracted_text=text)
    except MCPAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=exc.message)
    except MCPClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error extracting text from Drive file %s: %s", file_id, exc)
        raise HTTPException(status_code=500, detail="Internal error extracting text from Drive PDF")


@router.post("/generate", response_model=StudyPackOutput)
async def generate_from_drive_file(
    request: DriveGenerateRequest,
    x_drive_token: Optional[str] = Header(default=None, alias="X-Drive-Token"),
):
    """
    Ingest a Google Drive lecture PDF via MCP and pass it directly
    into the existing StudyPack generation pipeline.
    """
    effective_token = request.token or x_drive_token

    try:
        text_content = await mcp_client.read_document_text(
            file_id=request.file_id.strip(),
            token=effective_token,
        )
    except MCPAuthenticationError as exc:
        raise HTTPException(status_code=401, detail=exc.message)
    except MCPClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Source text from Google Drive document must be at least 50 characters.",
        )

    try:
        return generate_study_pack(text_content)
    except AIGenerationError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
