from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UtteranceSchema(BaseModel):
    id: Optional[str] = None
    speaker: str # Doctor, Patient
    text: str
    timestamp: Optional[str] = "00:00"
    confidence: Optional[float] = 0.95

class TranscriptCreate(BaseModel):
    session_id: str
    full_text: str
    dialogue: List[UtteranceSchema] = []
    duration_seconds: int = 0
    word_count: int = 0
    audio_url: Optional[str] = None

class TranscriptResponse(BaseModel):
    id: str
    session_id: str
    full_text: str
    dialogue: List[Dict[str, Any]]
    duration_seconds: int
    word_count: int
    audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
