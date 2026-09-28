import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class CaseDocument(Base):
    __tablename__ = "case_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), default="Clinical Document", nullable=False) # Clinical Note PDF, CMS-1500 EDI, Audio Transcript, Encounter Summary
    file_size_bytes = Column(Integer, default=10240, nullable=False)
    download_url = Column(String(500), nullable=True)
    uploaded_by = Column(String(255), default="System AI", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="documents")
