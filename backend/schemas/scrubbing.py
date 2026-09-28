from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ScrubbingIssueSchema(BaseModel):
    id: str
    rule_id: str
    rule_name: str
    severity: str # PASS, WARNING, ERROR
    category: str # Documentation, Coding, Billing, Compliance, Medical Necessity
    message: str
    suggested_action: str
    affected_code: Optional[str] = None

class ScrubbingResultResponse(BaseModel):
    id: str
    session_id: str
    total_checks: int
    passed_count: int
    warning_count: int
    error_count: int
    status: str
    issues: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
