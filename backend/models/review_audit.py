import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ReviewAudit(Base):
    __tablename__ = "review_audits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    code_suggestion_id = Column(String(36), ForeignKey("code_suggestions.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False) # APPROVE, MODIFY, REJECT
    previous_code = Column(String(50), nullable=False)
    new_code = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    reviewer_name = Column(String(255), default="Certified Coder", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("Session", back_populates="review_audits")
    code_suggestion = relationship("CodeSuggestion", back_populates="audits")
