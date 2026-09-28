import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    chief_complaint = Column(Text, nullable=False)
    symptoms = Column(JSON, default=list, nullable=False)
    duration = Column(String(255), nullable=False)
    relevant_history = Column(JSON, default=list, nullable=False)
    possible_diagnosis = Column(JSON, default=list, nullable=False)
    procedures = Column(JSON, default=list, nullable=False)
    medications = Column(JSON, default=list, nullable=False)
    additional_findings = Column(JSON, default=list, nullable=False)
    
    # SOAP Note Sections
    soap_subjective = Column(Text, nullable=True)
    soap_objective = Column(Text, nullable=True)
    soap_assessment = Column(Text, nullable=True)
    soap_plan = Column(Text, nullable=True)
    
    ai_disclaimer = Column(Text, default="DISCLAIMER: AI-generated clinical documentation draft. Requires licensed physician verification before billing.", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="clinical_note")
