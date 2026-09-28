from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CodeSuggestionBase(BaseModel):
    clinical_concept: str
    code_type: str = "ICD-10-CM"
    suggested_code: str
    description: str
    confidence: int = 90
    reasoning: str
    review_status: Optional[str] = "PENDING"

class CodeSuggestionCreate(CodeSuggestionBase):
    session_id: str

class CodeModifyRequest(BaseModel):
    modified_code: str
    modified_description: str
    reviewer_notes: str

class CodeRejectRequest(BaseModel):
    reason: str

class CodeApproveRequest(BaseModel):
    reviewer_notes: Optional[str] = "Approved by certified coder"

class CodeSuggestionResponse(CodeSuggestionBase):
    id: str
    session_id: str
    modified_code: Optional[str] = None
    modified_description: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
