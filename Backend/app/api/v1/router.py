"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter
from app.api.v1 import extract, generation, quiz, tutor, export, study_pack, drive, auth, agent

api_router = APIRouter()

api_router.include_router(agent.router, prefix="/agent", tags=["Multi-Agent"])
api_router.include_router(extract.router, prefix="/extract", tags=["Extraction"])
api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
api_router.include_router(tutor.router, prefix="/tutor", tags=["Tutor"])
api_router.include_router(export.router, prefix="/export", tags=["Export"])
api_router.include_router(study_pack.router, prefix="/study-pack", tags=["StudyPack Resources"])
api_router.include_router(drive.router, prefix="/drive", tags=["Google Drive MCP"])
api_router.include_router(auth.router, prefix="/auth", tags=["OAuth Authentication"])

