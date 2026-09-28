import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, GoogleLoginRequest, UserResponse, TokenResponse, UserProfileUpdate
from backend.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    require_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    email_clean = user_data.email.strip().lower()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please sign in instead."
        )
    
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=email_clean,
        hashed_password=hashed_pwd,
        full_name=user_data.full_name.strip(),
        role=user_data.role or "coder",
        employee_id=user_data.employee_id or f"EMP-{uuid.uuid4().hex[:6].upper()}",
        organization=user_data.organization or "Apex Health RCM Systems",
        department=user_data.department or "Clinical Revenue & Coding",
        specialization=user_data.specialization or "Outpatient & Inpatient Coding",
        phone=user_data.phone,
        is_active=True,
        last_login=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "email": new_user.email, "role": new_user.role})
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse.model_validate(new_user))

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    email_clean = login_data.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please create an account first."
        )
    
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again."
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))

@router.post("/google", response_model=TokenResponse)
def google_login(google_data: GoogleLoginRequest, db: Session = Depends(get_db)):
    email_clean = google_data.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    
    if not user:
        # Create new user for first-time Google sign-in
        random_pwd = uuid.uuid4().hex + uuid.uuid4().hex
        hashed_pwd = get_password_hash(random_pwd)
        user = User(
            email=email_clean,
            hashed_password=hashed_pwd,
            full_name=google_data.full_name.strip(),
            role=google_data.role or "coder",
            employee_id=f"EMP-GGL-{uuid.uuid4().hex[:4].upper()}",
            organization="Apex Health RCM Systems",
            department="Clinical Revenue & Coding",
            specialization="General Clinical Coding",
            is_active=True,
            last_login=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))

@router.post("/logout")
def logout():
    return {"success": True, "message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(require_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(require_current_user)):
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    update_dict = data.model_dump(exclude_unset=True)
    for k, v in update_dict.items():
        setattr(current_user, k, v)
        
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
