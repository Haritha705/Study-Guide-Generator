from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_parser import parse_pdf

router = APIRouter()

@router.post("/")
async def extract_content(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    text = parse_pdf(content)
    
    return {"extracted_text": text}
