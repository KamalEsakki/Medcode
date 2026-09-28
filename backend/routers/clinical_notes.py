from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.session import Session as ClinicalSession
from backend.models.transcript import Transcript
from backend.models.clinical_note import ClinicalNote
from backend.schemas.clinical_note import ClinicalNoteResponse
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/clinical-notes", tags=["Clinical Documentation"])

@router.post("/analyze/{session_id}", response_model=ClinicalNoteResponse)
def analyze_clinical_notes(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    transcript = db.query(Transcript).filter(Transcript.session_id == session_id).first()
    transcript_text = transcript.full_text if transcript else session.specialty

    # Extract clinical info with AI service
    extracted = ai_service.extract_clinical_information(
        transcript_text=transcript_text,
        patient_info={"name": session.patient_name, "age": session.patient_age, "specialty": session.specialty}
    )

    existing = db.query(ClinicalNote).filter(ClinicalNote.session_id == session_id).first()
    if existing:
        for k, v in extracted.items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        session.status = "analyzed"
        db.commit()
        return ClinicalNoteResponse.model_validate(existing)

    new_note = ClinicalNote(
        session_id=session_id,
        **extracted
    )
    db.add(new_note)
    session.status = "analyzed"
    db.commit()
    db.refresh(new_note)

    return ClinicalNoteResponse.model_validate(new_note)

@router.get("/{session_id}", response_model=ClinicalNoteResponse)
def get_clinical_note(session_id: str, db: Session = Depends(get_db)):
    note = db.query(ClinicalNote).filter(ClinicalNote.session_id == session_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinical note not found for session")
    return ClinicalNoteResponse.model_validate(note)
