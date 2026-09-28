from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.code_suggestion import CodeSuggestion
from backend.models.review_audit import ReviewAudit
from backend.models.user import User
from backend.schemas.coding import (
    CodeSuggestionResponse,
    CodeApproveRequest,
    CodeModifyRequest,
    CodeRejectRequest,
)
from backend.schemas.review import AllReviewsResponse, ReviewAuditResponse
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/reviews", tags=["Human Review Workflow"])

@router.get("", response_model=AllReviewsResponse)
def get_all_reviews(db: Session = Depends(get_db)):
    suggestions = db.query(CodeSuggestion).order_by(CodeSuggestion.created_at.desc()).all()
    audits = db.query(ReviewAudit).order_by(ReviewAudit.created_at.desc()).all()

    return AllReviewsResponse(
        suggestions=[CodeSuggestionResponse.model_validate(s) for s in suggestions],
        audits=[ReviewAuditResponse.model_validate(a) for a in audits],
    )

@router.post("/{code_id}/approve", response_model=CodeSuggestionResponse)
def approve_code(
    code_id: str,
    data: Optional[CodeApproveRequest] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    code = db.query(CodeSuggestion).filter(CodeSuggestion.id == code_id).first()
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code suggestion not found")
    
    reviewer_name = current_user.full_name if current_user else "Certified Coder"
    code.review_status = "APPROVED"
    code.reviewed_by = reviewer_name
    code.reviewed_at = datetime.utcnow()
    if data and data.reviewer_notes:
        code.reviewer_notes = data.reviewer_notes

    audit = ReviewAudit(
        session_id=code.session_id,
        code_suggestion_id=code.id,
        action="APPROVE",
        previous_code=code.suggested_code,
        note=data.reviewer_notes if data else "Approved as clinically accurate",
        reviewer_name=reviewer_name,
    )
    db.add(audit)
    db.commit()
    db.refresh(code)

    return CodeSuggestionResponse.model_validate(code)

@router.post("/{code_id}/modify", response_model=CodeSuggestionResponse)
def modify_code(
    code_id: str,
    data: CodeModifyRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    code = db.query(CodeSuggestion).filter(CodeSuggestion.id == code_id).first()
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code suggestion not found")
    
    reviewer_name = current_user.full_name if current_user else "Certified Coder"
    prev_code = code.suggested_code
    code.review_status = "MODIFIED"
    code.modified_code = data.modified_code
    code.modified_description = data.modified_description
    code.reviewer_notes = data.reviewer_notes
    code.reviewed_by = reviewer_name
    code.reviewed_at = datetime.utcnow()

    audit = ReviewAudit(
        session_id=code.session_id,
        code_suggestion_id=code.id,
        action="MODIFY",
        previous_code=prev_code,
        new_code=data.modified_code,
        note=data.reviewer_notes,
        reviewer_name=reviewer_name,
    )
    db.add(audit)
    db.commit()
    db.refresh(code)

    return CodeSuggestionResponse.model_validate(code)

@router.post("/{code_id}/reject", response_model=CodeSuggestionResponse)
def reject_code(
    code_id: str,
    data: CodeRejectRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    code = db.query(CodeSuggestion).filter(CodeSuggestion.id == code_id).first()
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code suggestion not found")
    
    reviewer_name = current_user.full_name if current_user else "Certified Coder"
    code.review_status = "REJECTED"
    code.reviewer_notes = data.reason
    code.reviewed_by = reviewer_name
    code.reviewed_at = datetime.utcnow()

    audit = ReviewAudit(
        session_id=code.session_id,
        code_suggestion_id=code.id,
        action="REJECT",
        previous_code=code.suggested_code,
        note=data.reason,
        reviewer_name=reviewer_name,
    )
    db.add(audit)
    db.commit()
    db.refresh(code)

    return CodeSuggestionResponse.model_validate(code)
