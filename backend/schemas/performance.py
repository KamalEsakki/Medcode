from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PerformanceDailyTrend(BaseModel):
    date: str
    cases_completed: int
    codes_reviewed: int
    clean_claim_rate: float
    avg_review_mins: float

class PerformanceMetricsResponse(BaseModel):
    user_id: str
    user_name: str
    role: str
    timeframe: str # daily, weekly, monthly
    
    # Core Scrubber Work Metrics
    cases_assigned: int
    cases_completed: int
    cases_in_progress: int
    cases_approved: int
    cases_returned: int
    total_codes_reviewed: int
    scrubbing_issues_flagged: int
    
    # Quality & Speed Ratios
    clean_claim_rate: float # e.g. 94.5%
    completion_rate: float # e.g. 91.2%
    avg_review_time_minutes: float # e.g. 4.8 mins
    
    # Daily Trend Chart Data
    daily_trend: List[PerformanceDailyTrend]
    specialty_distribution: List[Dict[str, Any]]
