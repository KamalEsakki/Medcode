from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.schemas.session import SessionResponse

class ScrubbingSummary(BaseModel):
    pass_count: int
    warning_count: int
    error_count: int

class ActivityItemResponse(BaseModel):
    id: str
    time: str
    action: str
    details: Optional[str] = None
    session_id: Optional[str] = None
    session_code: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    # Daily Workload Cards
    assigned_cases: int = 0
    in_progress_cases: int = 0
    completed_today: int = 0
    pending_reviews: int = 0
    approved_cases: int = 0
    returned_cases: int = 0
    
    # Key Metrics
    total_encounters_reviewed: int = 0
    total_codes_reviewed: int = 0
    scrubbing_issues_found: int = 0
    average_review_time_mins: float = 4.2
    clean_claim_rate: float = 94.5
    completion_rate: float = 92.0
    
    # Overview / Legacy Compat
    total_sessions: int = 0
    transcripts_processed: int = 0
    code_suggestions: int = 0
    scrubbing_issues: int = 0
    approved_reviews: int = 0
    accuracy_rate: float = 96.4
    pass_rate: float = 92.0
    
    recent_sessions: List[SessionResponse] = []
    my_active_cases: List[SessionResponse] = []
    activity_timeline: List[ActivityItemResponse] = []
    scrubbing_summary: Dict[str, int] = {"pass": 0, "warning": 0, "error": 0}
    codes_by_category: List[Dict[str, Any]] = []
    weekly_trend: List[Dict[str, Any]] = []
