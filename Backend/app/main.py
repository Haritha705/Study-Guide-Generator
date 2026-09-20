"""FastAPI application entry point for StudyPack AI."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.models import attempt, studypack, user  # Import models so SQLAlchemy metadata is aware of them
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # --- Startup ---
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    init_db()
    logger.info("Database tables initialized.")
    yield
    # --- Shutdown ---
    logger.info(f"Shutting down {settings.PROJECT_NAME}.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent study material generator and dynamic quiz engine.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
register_exception_handlers(app)

# Include API routes
from app.api.v1.study_pack import router as study_pack_router

app.include_router(api_router, prefix="/api/v1")
app.include_router(study_pack_router, prefix="/study-pack", tags=["StudyPack Resources"])


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} Backend"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
