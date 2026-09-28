import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class ScrubbingResult(Base):
    __tablename__ = "scrubbing_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_checks = Column(Integer, default=12, nullable=False)
    passed_count = Column(Integer, default=10, nullable=False)
    warning_count = Column(Integer, default=2, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="PASS", nullable=False) # PASS, WARNING, ERROR
    issues_json = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="scrubbing_result")
