"""Custom exceptions and FastAPI exception handler registration."""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class StudyPackException(Exception):
    """Base exception for all StudyPack AI errors."""

    def __init__(self, message: str = "An unexpected error occurred.", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class PDFProcessingError(StudyPackException):
    """Raised when PDF extraction or validation fails."""

    def __init__(self, message: str = "Failed to process the uploaded PDF."):
        super().__init__(message=message, status_code=400)


class AIGenerationError(StudyPackException):
    """Raised when the AI model fails to generate valid output."""

    def __init__(self, message: str = "AI generation failed. Please try again."):
        super().__init__(message=message, status_code=502)


class QuizEvaluationError(StudyPackException):
    """Raised when quiz grading encounters invalid data."""

    def __init__(self, message: str = "Failed to evaluate quiz submission."):
        super().__init__(message=message, status_code=422)


class RAGRetrievalError(StudyPackException):
    """Raised when the RAG pipeline fails to retrieve context."""

    def __init__(self, message: str = "Failed to retrieve context for the question."):
        super().__init__(message=message, status_code=500)


class RateLimitError(StudyPackException):
    """Raised when a rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded. Please wait before retrying."):
        super().__init__(message=message, status_code=429)


class ExportError(StudyPackException):
    """Raised when PDF or CSV export fails."""

    def __init__(self, message: str = "Failed to generate export file."):
        super().__init__(message=message, status_code=500)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI app."""

    @app.exception_handler(StudyPackException)
    async def studypack_exception_handler(request: Request, exc: StudyPackException):
        logger.error(f"StudyPackException: {exc.message} | Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": type(exc).__name__,
                "message": exc.message,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception at {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected internal error occurred.",
                "path": str(request.url.path),
            },
        )
