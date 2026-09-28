import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class CodeSuggestion(Base):
    __tablename__ = "code_suggestions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    clinical_concept = Column(String(255), nullable=False)
    code_type = Column(String(50), default="ICD-10-CM", nullable=False) # ICD-10-CM, CPT, HCPCS
    suggested_code = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    confidence = Column(Integer, default=90, nullable=False) # 0-100
    reasoning = Column(Text, nullable=False)
    
    # Human Review Status
    review_status = Column(String(50), default="PENDING", nullable=False) # PENDING, APPROVED, MODIFIED, REJECTED
    modified_code = Column(String(50), nullable=True)
    modified_description = Column(Text, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="code_suggestions")
    audits = relationship("ReviewAudit", back_populates="code_suggestion", cascade="all, delete-orphan")
