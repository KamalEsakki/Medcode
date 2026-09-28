from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ZoomValidateRequest(BaseModel):
    meeting_url: str

class ZoomValidateResponse(BaseModel):
    is_valid: bool
    meeting_id: Optional[str] = None
    passcode: Optional[str] = None
    normalized_url: Optional[str] = None
    message: str

class ZoomJoinRequest(BaseModel):
    meeting_url: str
    patient_name: Optional[str] = "Demo Patient"
    patient_age: Optional[int] = 45
    patient_gender: Optional[str] = "Male"
    doctor_name: Optional[str] = "Dr. Sarah Lin, MD"
    specialty: Optional[str] = "Cardiology"
    session_type: Optional[str] = "Zoom Telehealth Consultation"

class ZoomDialogueItem(BaseModel):
    speaker: str  # "Doctor" or "Patient"
    text: str
    timestamp: str
    consultationId: Optional[str] = None

class ZoomStatusResponse(BaseModel):
    session_id: str
    session_code: str
    zoom_meeting_id: Optional[str] = None
    zoom_meeting_url: Optional[str] = None
    connection_status: str  # "WAITING", "CONNECTING", "CONNECTED", "RECEIVING_DATA", "COMPLETED"
    audio_status: str  # "IDLE", "STREAMING", "MUTED", "COMPLETED"
    transcript_status: str  # "WAITING", "STREAMING", "READY_FOR_ANALYSIS", "COMPLETED"
    is_demo_mode: bool
    provenance_label: str
    patient_name: str
    doctor_name: str
    specialty: str

class ZoomWebhookEvent(BaseModel):
    event: str
    payload: dict = Field(default_factory=dict)
