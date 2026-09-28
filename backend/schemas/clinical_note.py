from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClinicalNoteBase(BaseModel):
    chief_complaint: str
    symptoms: List[str] = []
    duration: str
    relevant_history: List[str] = []
    possible_diagnosis: List[str] = []
    procedures: List[str] = []
    medications: List[str] = []
    additional_findings: List[str] = []
    soap_subjective: Optional[str] = None
    soap_objective: Optional[str] = None
    soap_assessment: Optional[str] = None
    soap_plan: Optional[str] = None
    ai_disclaimer: Optional[str] = "DISCLAIMER: AI-generated clinical documentation draft. Requires licensed physician verification before billing."

class ClinicalNoteCreate(ClinicalNoteBase):
    session_id: str

class ClinicalNoteResponse(ClinicalNoteBase):
    id: str
    session_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
