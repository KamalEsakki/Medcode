from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.session import Session as ClinicalSession
from backend.models.clinical_note import ClinicalNote
from backend.models.code_suggestion import CodeSuggestion
from backend.schemas.coding import CodeSuggestionResponse
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/coding", tags=["Medical Coding"])

@router.post("/analyze/{session_id}", response_model=List[CodeSuggestionResponse])
def generate_coding(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    note = db.query(ClinicalNote).filter(ClinicalNote.session_id == session_id).first()
    note_dict = {
        "chief_complaint": note.chief_complaint if note else session.specialty,
        "soap_assessment": note.soap_assessment if note else session.session_type,
    }

    suggestions = ai_service.generate_code_suggestions(note_dict)

    # Clean old suggestions for this session
    db.query(CodeSuggestion).filter(CodeSuggestion.session_id == session_id).delete()

    created_list = []
    for item in suggestions:
        cs = CodeSuggestion(
            session_id=session_id,
            clinical_concept=item["clinical_concept"],
            code_type=item.get("code_type", "ICD-10-CM"),
            suggested_code=item["suggested_code"],
            description=item["description"],
            confidence=item.get("confidence", 90),
            reasoning=item["reasoning"],
            review_status="PENDING",
        )
        db.add(cs)
        created_list.append(cs)

    db.commit()
    for cs in created_list:
        db.refresh(cs)

    return [CodeSuggestionResponse.model_validate(cs) for cs in created_list]

@router.get("/{session_id}", response_model=List[CodeSuggestionResponse])
def get_coding(session_id: str, db: Session = Depends(get_db)):
    codes = db.query(CodeSuggestion).filter(CodeSuggestion.session_id == session_id).all()
    return [CodeSuggestionResponse.model_validate(c) for c in codes]
