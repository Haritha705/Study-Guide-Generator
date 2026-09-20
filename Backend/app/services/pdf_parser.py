import io
import logging
from pypdf import PdfReader
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Default limit increased to 100 pages to comfortably cover 50 to 70+ page lecture materials
MAX_PDF_PAGES = 100


def parse_pdf(file_bytes: bytes, max_pages: int = MAX_PDF_PAGES) -> str:
    """
    Parses and extracts text from a PDF file.
    Supports comprehensive lecture notes and textbooks up to `max_pages` (default 100).
    """
    try:
        pdf = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted PDF file: {exc}")

    total_pages = len(pdf.pages)
    if total_pages == 0:
        raise HTTPException(status_code=400, detail="PDF document is empty.")

    if total_pages > max_pages:
        raise HTTPException(
            status_code=400,
            detail=f"PDF has {total_pages} pages, which exceeds the limit of {max_pages} pages.",
        )

    logger.info("Parsing PDF with %s pages (limit: %s)...", total_pages, max_pages)

    text_chunks = []
    for idx, page in enumerate(pdf.pages):
        try:
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_chunks.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")
        except Exception as page_err:
            logger.warning("Could not extract text from page %s: %s", idx + 1, page_err)
            continue

    text = "\n\n".join(text_chunks).strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF. Make sure the document contains selectable text.",
        )

    logger.info("Successfully extracted %s characters from %s pages.", len(text), total_pages)
    return text
