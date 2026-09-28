import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False) # OPENED_CASE, ANALYZED_TRANSCRIPT, MODIFIED_CODE, APPROVED_CLAIM, RETURNED_CLAIM, VOICE_COMMAND, GENERATED_CODES
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    session = relationship("Session", back_populates="activity_logs")
