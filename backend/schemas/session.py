from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SessionBase(BaseModel):
    patient_name: str
    patient_age: int = 45
    patient_gender: str = "Male"
    doctor_name: str = "Dr. Sarah Lin, MD"
    specialty: str = "Cardiology"
    session_type: str = "Clinical Consultation"
    consultation_source: Optional[str] = "Zoom"
    priority: Optional[str] = "NORMAL"
    stage: Optional[str] = "NEW"
    total_charges: Optional[float] = 320.00
    zoom_meeting_url: Optional[str] = None
    zoom_meeting_id: Optional[str] = None
    teams_meeting_url: Optional[str] = None
    teams_meeting_id: Optional[str] = None
    assigned_scrubber_id: Optional[str] = None
    assigned_scrubber_name: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    session_type: Optional[str] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    priority: Optional[str] = None
    total_charges: Optional[float] = None
    assigned_scrubber_id: Optional[str] = None
    assigned_scrubber_name: Optional[str] = None
    zoom_meeting_url: Optional[str] = None
    zoom_meeting_id: Optional[str] = None
    teams_meeting_url: Optional[str] = None
    teams_meeting_id: Optional[str] = None

class TextToCodeRequest(BaseModel):
    clinical_text: str
    patient_name: Optional[str] = "Walk-in Consultation Patient"
    patient_age: Optional[int] = 52
    patient_gender: Optional[str] = "Female"
    doctor_name: Optional[str] = "Dr. Sarah Lin, MD"
    specialty: Optional[str] = "General Practice"
    session_type: Optional[str] = "Text / Dictation Intake"
    priority: Optional[str] = "NORMAL"

class CaseStageUpdateRequest(BaseModel):
    stage: str # NEW, IN_PROGRESS, CODING_REVIEW, SCRUBBING, WAITING_FOR_REVIEW, RETURNED, APPROVED, COMPLETED
    note: Optional[str] = None

class SessionResponse(SessionBase):
    id: str
    session_code: str
    status: str
    stage: str = "NEW"
    priority: str = "NORMAL"
    consultation_source: str = "Zoom"
    total_charges: float = 320.00
    assigned_scrubber_id: Optional[str] = None
    assigned_scrubber_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    transcript_count: Optional[int] = 0
    code_count: Optional[int] = 0
    scrubbing_status: Optional[str] = "PASS"
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True
