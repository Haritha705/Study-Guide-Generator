from fastapi import APIRouter
from app.api.v1 import extract, generation, quiz, tutor, export

api_router = APIRouter()
api_router.include_router(extract.router, prefix="/extract", tags=["Extraction"])
api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
# api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
# api_router.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])
# api_router.include_router(export.router, prefix="/export", tags=["Export"])
