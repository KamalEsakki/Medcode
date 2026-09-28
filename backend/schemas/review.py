from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.schemas.coding import CodeSuggestionResponse

class ReviewAuditResponse(BaseModel):
    id: str
    session_id: str
    code_suggestion_id: str
    action: str
    previous_code: str
    new_code: Optional[str] = None
    note: Optional[str] = None
    reviewer_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class AllReviewsResponse(BaseModel):
    suggestions: List[CodeSuggestionResponse]
    audits: List[ReviewAuditResponse]
