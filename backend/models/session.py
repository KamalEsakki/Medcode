import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_name = Column(String(255), nullable=False)
    patient_age = Column(Integer, default=45, nullable=False)
    patient_gender = Column(String(20), default="Male", nullable=False)
    doctor_name = Column(String(255), default="Dr. Sarah Lin, MD", nullable=False)
    specialty = Column(String(100), default="General Practice", nullable=False)
    session_type = Column(String(100), default="Clinical Consultation", nullable=False)
    
    # Status & Workflow Stage
    status = Column(String(50), default="recording", nullable=False) # recording, completed, analyzed, reviewed, returned, approved
    stage = Column(String(50), default="NEW", nullable=False) # NEW, IN_PROGRESS, CODING_REVIEW, SCRUBBING, WAITING_FOR_REVIEW, RETURNED, APPROVED, COMPLETED
    priority = Column(String(20), default="NORMAL", nullable=False) # URGENT, HIGH, NORMAL, LOW
    
    # Consultation Sources
    consultation_source = Column(String(50), default="Zoom", nullable=False) # Zoom, Microsoft Teams, Manual Text, Audio Upload
    zoom_meeting_url = Column(String(500), nullable=True)
    zoom_meeting_id = Column(String(100), nullable=True)
    teams_meeting_url = Column(String(500), nullable=True)
    teams_meeting_id = Column(String(100), nullable=True)
    
    # Assignment & Financials
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_scrubber_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_scrubber_name = Column(String(255), nullable=True)
    total_charges = Column(Float, default=320.00, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions", foreign_keys=[user_id])
    assigned_scrubber = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_scrubber_id])
    transcript = relationship("Transcript", back_populates="session", uselist=False, cascade="all, delete-orphan")
    clinical_note = relationship("ClinicalNote", back_populates="session", uselist=False, cascade="all, delete-orphan")
    code_suggestions = relationship("CodeSuggestion", back_populates="session", cascade="all, delete-orphan")
    scrubbing_result = relationship("ScrubbingResult", back_populates="session", uselist=False, cascade="all, delete-orphan")
    review_audits = relationship("ReviewAudit", back_populates="session", cascade="all, delete-orphan")
    documents = relationship("CaseDocument", back_populates="session", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="session", cascade="all, delete-orphan")
