"""Export API endpoints — PDF and CSV download."""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List
import io

from app.services.pdf_exporter import generate_pdf
from app.services.csv_exporter import generate_csv
from app.core.exceptions import ExportError

router = APIRouter()


@router.post("/pdf")
async def export_pdf(content: Dict[str, Any] = Body(...)):
    """
    Generate and download a formatted PDF of the study pack.

    Request body should contain the study pack data:
    - notes, mcqs, glossary, short_answers, recommended_study_order

    Returns:
        Streaming PDF file download.
    """
    if not content:
        raise HTTPException(status_code=400, detail="No content provided for PDF export.")

    try:
        pdf_bytes = generate_pdf(content)

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=studypack.pdf",
                "Content-Length": str(len(pdf_bytes)),
            },
        )
    except ExportError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@router.post("/csv")
async def export_csv(mcqs: List[Dict[str, Any]] = Body(...)):
    """
    Generate and download MCQs as a CSV file.

    Request body should be a list of MCQ objects matching MCQItem schema.

    Returns:
        Streaming CSV file download.
    """
    if not mcqs:
        raise HTTPException(status_code=400, detail="No MCQs provided for CSV export.")

    try:
        csv_content = generate_csv(mcqs)

        return StreamingResponse(
            io.BytesIO(csv_content.encode("utf-8")),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=mcqs.csv",
            },
        )
    except ExportError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")
