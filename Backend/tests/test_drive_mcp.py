"""Unit and integration tests for Google Drive MCP integration."""

import base64
import io
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app
from app.services.mcp_client import (
    mcp_client,
    MCPAuthenticationError,
    MCPClientError,
)

client = TestClient(app)


def _create_sample_pdf_bytes(text: str = "This is a test lecture on Quantum Mechanics and Wave Particle Duality.") -> bytes:
    """Helper to create valid in-memory PDF bytes with text."""
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, text)
    c.save()
    return buf.getvalue()


# 1. Live MCP Connection Status Test
@pytest.mark.asyncio
async def test_live_mcp_connection_status():
    """Verify live connectivity with official Google Drive MCP server."""
    status = await mcp_client.connect()
    assert status["connected"] is True
    assert status["status"] == "ready"
    assert status["tools_count"] > 0
    assert "search_files" in status["tools"]
    assert "download_file_content" in status["tools"]


def test_endpoint_drive_status():
    """Test GET /api/v1/drive/status."""
    response = client.get("/api/v1/drive/status")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["server_url"] == "https://drivemcp.googleapis.com/mcp/v1"
    assert "search_files" in data["tools"]


# 2. Authentication Error Handling Tests
def test_drive_files_missing_token_returns_401():
    """Test GET /api/v1/drive/files returns 401 when no token is provided."""
    with patch.object(mcp_client, "_resolve_token", return_value=""):
        response = client.get("/api/v1/drive/files?query=lecture")
        assert response.status_code == 401
        assert "token" in response.json()["detail"].lower()


def test_drive_extract_missing_token_returns_401():
    """Test GET /api/v1/drive/files/{file_id}/extract returns 401 when no token."""
    with patch.object(mcp_client, "_resolve_token", return_value=""):
        response = client.get("/api/v1/drive/files/file-123/extract")
        assert response.status_code == 401


# 3. Google Drive Search via MCP (Mocked response)
def test_drive_search_success():
    """Test GET /api/v1/drive/files with mocked MCP tool response."""
    mock_files = [
        {"id": "doc_1", "name": "Physics_Lecture_1.pdf", "mimeType": "application/pdf"},
        {"id": "doc_2", "name": "Chemistry_Notes.pdf", "mimeType": "application/pdf"},
    ]

    with patch.object(mcp_client, "search_files", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_files
        response = client.get("/api/v1/drive/files?query=Physics", headers={"X-Drive-Token": "test-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert data["files"][0]["name"] == "Physics_Lecture_1.pdf"


# 4. Read/Download PDF from Google Drive via MCP
def test_drive_pdf_extract_success():
    """Test reading and parsing a PDF downloaded from Google Drive via MCP."""
    sample_text = "Thermodynamics Lecture Notes: Entropy and the Second Law of Thermodynamics."
    pdf_bytes = _create_sample_pdf_bytes(sample_text)

    with patch.object(mcp_client, "download_file_bytes", new_callable=AsyncMock) as mock_dl:
        mock_dl.return_value = pdf_bytes
        response = client.get(
            "/api/v1/drive/files/lecture-pdf-id/extract",
            headers={"X-Drive-Token": "test-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == "lecture-pdf-id"
        assert "Thermodynamics" in data["extracted_text"]


# 5. StudyPack Generation from Drive PDF
def test_drive_generate_studypack_success():
    """Test POST /api/v1/drive/generate pipeline integration."""
    lecture_text = (
        "Introduction to Computer Science and Object Oriented Programming. "
        "Key concepts include Abstraction, Encapsulation, Inheritance, and Polymorphism. "
        "These principles enable scalable and maintainable software design."
    )
    pdf_bytes = _create_sample_pdf_bytes(lecture_text)

    mock_output = {
        "summary": "Overview of OOP principles.",
        "recommended_study_order": ["OOP Basics", "Encapsulation", "Inheritance"],
        "notes": [
            {
                "topic": "OOP",
                "content": ["Object Oriented Programming concepts."],
                "highlights": [{"type": "Concept", "text": "Encapsulation"}],
            }
        ],
        "glossary": [{"term": "OOP", "definition": "Object Oriented Programming"}],
        "flashcards": [{"term": "Encapsulation", "definition": "Data hiding"}],
        "mcqs": [],
        "short_answers": [],
    }

    with patch.object(mcp_client, "download_file_bytes", new_callable=AsyncMock) as mock_dl, \
         patch("app.api.v1.drive.generate_study_pack", return_value=mock_output) as mock_gen:
        mock_dl.return_value = pdf_bytes

        response = client.post(
            "/api/v1/drive/generate",
            json={"file_id": "oop-lecture-id", "token": "test-token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Overview of OOP principles."
        mock_gen.assert_called_once()


# 6. Verify Local PDF Upload Remains Working Exactly As Before
def test_local_pdf_upload_remains_functional():
    """Confirm POST /api/v1/extract/ continues to work for uploaded local files."""
    sample_text = "Local Lecture Upload: Machine learning models require clean training datasets."
    pdf_bytes = _create_sample_pdf_bytes(sample_text)

    files = {"file": ("local_lecture.pdf", pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/extract/", files=files)
    assert response.status_code == 200
    assert "Machine learning" in response.json()["extracted_text"]
