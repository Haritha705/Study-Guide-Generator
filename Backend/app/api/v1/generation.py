from fastapi import APIRouter, Body, HTTPException
from app.schemas.studypack import StudyPackOutput
from app.services.ai_pipeline import generate_study_pack
from app.core.exceptions import AIGenerationError

router = APIRouter()

@router.post("/", response_model=StudyPackOutput)
async def generate_pack(text_content: str = Body(..., embed=True)):
    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Source text must be at least 50 characters.",
        )

    try:
        return generate_study_pack(text_content)
    except AIGenerationError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
