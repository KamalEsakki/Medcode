import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="coder", nullable=False) # coder, auditor, physician, admin
    employee_id = Column(String(50), default="EMP-8021", nullable=True)
    organization = Column(String(255), default="Apex Health RCM Systems", nullable=True)
    department = Column(String(100), default="Clinical Revenue & Coding", nullable=True)
    specialization = Column(String(100), default="Outpatient & Inpatient Coding", nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("Session", back_populates="user", foreign_keys="Session.user_id", cascade="all, delete-orphan")
    assigned_cases = relationship("Session", back_populates="assigned_scrubber", foreign_keys="Session.assigned_scrubber_id")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
