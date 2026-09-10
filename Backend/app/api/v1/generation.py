from fastapi import APIRouter, Body
from app.schemas.studypack import StudyPackOutput
from app.services.ai_pipeline import generate_study_pack

router = APIRouter()

@router.post("/", response_model=StudyPackOutput)
async def generate_pack(text_content: str = Body(..., embed=True)):
    result = generate_study_pack(text_content)
    return result
