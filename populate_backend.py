import os

base_dir = r"c:\Users\Haritha\OneDrive\Desktop\Study-APP\Backend\app"

files_to_populate = {
    "config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyPack AI"
    ANTHROPIC_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    VECTOR_STORE_PROVIDER: str = "memory"
    
    class Config:
        env_file = ".env"

settings = Settings()
""",
    "main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} Backend"}
""",
    "api/v1/router.py": """from fastapi import APIRouter
from app.api.v1 import extract, generation, quiz, tutor, export

api_router = APIRouter()
api_router.include_router(extract.router, prefix="/extract", tags=["Extraction"])
api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
# api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
# api_router.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])
# api_router.include_router(export.router, prefix="/export", tags=["Export"])
""",
    "api/v1/extract.py": """from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_parser import parse_pdf

router = APIRouter()

@router.post("/")
async def extract_content(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    content = await file.read()
    text = parse_pdf(content)
    
    return {"extracted_text": text}
""",
    "api/v1/generation.py": """from fastapi import APIRouter, Body
from app.schemas.studypack import StudyPackOutput
from app.services.ai_pipeline import generate_study_pack

router = APIRouter()

@router.post("/", response_model=StudyPackOutput)
async def generate_pack(text_content: str = Body(..., embed=True)):
    result = generate_study_pack(text_content)
    return result
""",
    "services/pdf_parser.py": """from pypdf import PdfReader
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
            text += page_text + "\\n"
            
    if not text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")
        
    return text
""",
    "core/constants.py": """
SYSTEM_PROMPT = "You are an expert AI tutor."
DIFFICULTY_RATIO = {"Easy": 7, "Medium": 7, "Hard": 6}
"""
}

for file_rel, content in files_to_populate.items():
    file_path = os.path.join(base_dir, file_rel)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

print("Backend files populated successfully!")
