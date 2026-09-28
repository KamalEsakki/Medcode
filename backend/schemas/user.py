from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[str] = "coder" # coder, auditor, physician, admin
    employee_id: Optional[str] = "EMP-8021"
    organization: Optional[str] = "Apex Health RCM Systems"
    department: Optional[str] = "Clinical Revenue & Coding"
    specialization: Optional[str] = "Outpatient & Inpatient Coding"
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    email: EmailStr
    full_name: str
    google_id: Optional[str] = None
    role: Optional[str] = "coder"

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
