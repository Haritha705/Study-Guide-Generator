from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from pypdf import PdfReader
import io
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from schemas import StudyPackOutput

app = FastAPI(title="StudyPack AI API")

# Configure CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to StudyPack AI Backend"}

@app.post("/api/extract", response_model=StudyPackOutput)
async def extract_content(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Read PDF
    content = await file.read()
    pdf = PdfReader(io.BytesIO(content))
    
    # Validate page count <= 15
    if len(pdf.pages) > 15:
        raise HTTPException(status_code=400, detail="PDF exceeds 15 pages limit.")
    if len(pdf.pages) == 0:
        raise HTTPException(status_code=400, detail="PDF is empty.")
    
    # Extract text
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
            
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF (might be a scanned image).")

    # TODO: Implement LangChain orchestration with Claude/Mistral to generate structured output.
    # For now, return a placeholder to ensure the pipeline is wired up.
    
    return StudyPackOutput(
        recommended_study_order=["Topic 1"],
        notes=[],
        glossary=[],
        mcqs=[],
        short_answers=[]
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
