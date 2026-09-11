"""Input schemas for extraction and generation requests."""

from pydantic import BaseModel, Field
from typing import Optional


class TextInput(BaseModel):
    """Schema for raw text input (paste mode)."""
    text_content: str = Field(
        ...,
        min_length=50,
        max_length=100000,
        description="Raw text content from a syllabus or lecture notes."
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional title for the study pack."
    )


class PDFUploadResponse(BaseModel):
    """Response schema after successful PDF text extraction."""
    extracted_text: str = Field(..., description="Extracted raw text from the PDF.")
    page_count: int = Field(..., ge=1, description="Number of pages processed.")
    char_count: int = Field(..., ge=1, description="Total character count of extracted text.")


class GenerationRequest(BaseModel):
    """Schema for requesting study pack generation from extracted text."""
    text_content: str = Field(
        ...,
        min_length=50,
        description="Source text to generate study materials from."
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional title for the generated study pack."
    )
    include_mcqs: bool = Field(True, description="Whether to generate MCQs.")
    include_saqs: bool = Field(True, description="Whether to generate short answer questions.")
    include_glossary: bool = Field(True, description="Whether to generate a glossary.")
