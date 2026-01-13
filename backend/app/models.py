"""Pydantic models for API requests and responses"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    file_type: str
    size: int

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class SourceReference(BaseModel):
    document_id: str
    document_name: str
    page: Optional[int] = None
    excerpt: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference]
    confidence: str
    session_id: str
