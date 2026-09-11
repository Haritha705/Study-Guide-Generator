from pydantic import BaseModel, Field
from typing import List, Literal

class Highlight(BaseModel):
    type: Literal["Important", "Definition", "Concept", "Remember"]
    text: str

class NoteItem(BaseModel):
    topic: str
    content: List[str]
    highlights: List[Highlight]

class GlossaryItem(BaseModel):
    term: str
    definition: str

class FlashcardItem(BaseModel):
    term: str
    definition: str

class MCQItem(BaseModel):
    id: int
    question: str
    options: List[str]
    answer: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    topic: str
    explanation: str

class SAQItem(BaseModel):
    question: str
    model_answer: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    topic: str

class StudyPackOutput(BaseModel):
    summary: str
    recommended_study_order: List[str]
    notes: List[NoteItem]
    glossary: List[GlossaryItem]
    flashcards: List[FlashcardItem]
    mcqs: List[MCQItem]
    short_answers: List[SAQItem]
