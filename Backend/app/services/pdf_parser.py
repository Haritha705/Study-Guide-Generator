from pypdf import PdfReader
import io
from fastapi import HTTPException

def parse_pdf(file_bytes: bytes) -> str:
    pdf = PdfReader(io.BytesIO(file_bytes))
    
    if len(pdf.pages) > 15:
        raise HTTPException(status_code=400, detail="PDF exceeds 15 pages limit.")
    if len(pdf.pages) == 0:
        raise HTTPException(status_code=400, detail="PDF is empty.")
    
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
            
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")
        
    return text
