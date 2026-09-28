from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.session import Session as ClinicalSession
from backend.models.clinical_note import ClinicalNote
from backend.models.code_suggestion import CodeSuggestion
from backend.models.scrubbing_result import ScrubbingResult
from backend.schemas.scrubbing import ScrubbingResultResponse
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/scrubbing", tags=["Claim Scrubbing Engine"])

@router.post("/run/{session_id}", response_model=ScrubbingResultResponse)
def run_scrubbing(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    note = db.query(ClinicalNote).filter(ClinicalNote.session_id == session_id).first()
    note_dict = {
        "chief_complaint": note.chief_complaint if note else "",
        "symptoms": note.symptoms if note else [],
    }

    codes = db.query(CodeSuggestion).filter(CodeSuggestion.session_id == session_id).all()
    code_dicts = [
        {"suggested_code": c.suggested_code, "code_type": c.code_type, "clinical_concept": c.clinical_concept}
        for c in codes
    ]

    scrub_out = ai_service.generate_scrubbing_warnings(note_dict, code_dicts)

    existing = db.query(ScrubbingResult).filter(ScrubbingResult.session_id == session_id).first()
    if existing:
        existing.total_checks = scrub_out["total_checks"]
        existing.passed_count = scrub_out["passed_count"]
        existing.warning_count = scrub_out["warning_count"]
        existing.error_count = scrub_out["error_count"]
        existing.status = scrub_out["status"]
        existing.issues_json = scrub_out["issues"]
        db.commit()
        db.refresh(existing)
        return ScrubbingResultResponse(
            id=existing.id,
            session_id=existing.session_id,
            total_checks=existing.total_checks,
            passed_count=existing.passed_count,
            warning_count=existing.warning_count,
            error_count=existing.error_count,
            status=existing.status,
            issues=existing.issues_json,
            created_at=existing.created_at,
        )

    new_result = ScrubbingResult(
        session_id=session_id,
        total_checks=scrub_out["total_checks"],
        passed_count=scrub_out["passed_count"],
        warning_count=scrub_out["warning_count"],
        error_count=scrub_out["error_count"],
        status=scrub_out["status"],
        issues_json=scrub_out["issues"],
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return ScrubbingResultResponse(
        id=new_result.id,
        session_id=new_result.session_id,
        total_checks=new_result.total_checks,
        passed_count=new_result.passed_count,
        warning_count=new_result.warning_count,
        error_count=new_result.error_count,
        status=new_result.status,
        issues=new_result.issues_json,
        created_at=new_result.created_at,
    )

@router.get("/{session_id}", response_model=ScrubbingResultResponse)
def get_scrubbing(session_id: str, db: Session = Depends(get_db)):
    result = db.query(ScrubbingResult).filter(ScrubbingResult.session_id == session_id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scrubbing result not found for session")
    return ScrubbingResultResponse(
        id=result.id,
        session_id=result.session_id,
        total_checks=result.total_checks,
        passed_count=result.passed_count,
        warning_count=result.warning_count,
        error_count=result.error_count,
        status=result.status,
        issues=result.issues_json,
        created_at=result.created_at,
    )
