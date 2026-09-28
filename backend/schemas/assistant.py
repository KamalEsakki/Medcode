from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class AssistantCommandRequest(BaseModel):
    query: str
    current_case_id: Optional[str] = None
    current_path: Optional[str] = None

class AssistantCommandResponse(BaseModel):
    intent: str # SUMMARIZE_CASE, SHOW_ISSUES, EXPLAIN_CODE, NAVIGATE_CASES, SHOW_PERFORMANCE, APPROVE_CASE, GENERAL_QUERY
    response_text: str
    suggested_action: Optional[str] = None
    navigate_to: Optional[str] = None
    data_payload: Optional[Dict[str, Any]] = None
