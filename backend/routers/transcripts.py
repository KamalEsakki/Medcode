from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.transcript import Transcript
from backend.models.session import Session as ClinicalSession
from backend.schemas.transcript import TranscriptCreate, TranscriptResponse

router = APIRouter(prefix="/transcripts", tags=["Transcripts"])

@router.post("", response_model=TranscriptResponse)
def save_transcript(data: TranscriptCreate, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == data.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    dialogue_dicts = [u.model_dump() for u in data.dialogue]
    
    existing = db.query(Transcript).filter(Transcript.session_id == data.session_id).first()
    if existing:
        existing.full_text = data.full_text
        existing.dialogue_json = dialogue_dicts
        existing.duration_seconds = data.duration_seconds
        existing.word_count = data.word_count or len(data.full_text.split())
        existing.audio_url = data.audio_url
        db.commit()
        db.refresh(existing)
        return TranscriptResponse(
            id=existing.id,
            session_id=existing.session_id,
            full_text=existing.full_text,
            dialogue=existing.dialogue_json,
            duration_seconds=existing.duration_seconds,
            word_count=existing.word_count,
            audio_url=existing.audio_url,
            created_at=existing.created_at,
        )

    new_transcript = Transcript(
        session_id=data.session_id,
        full_text=data.full_text,
        dialogue_json=dialogue_dicts,
        duration_seconds=data.duration_seconds,
        word_count=data.word_count or len(data.full_text.split()),
        audio_url=data.audio_url,
    )
    db.add(new_transcript)
    session.status = "completed"
    db.commit()
    db.refresh(new_transcript)

    return TranscriptResponse(
        id=new_transcript.id,
        session_id=new_transcript.session_id,
        full_text=new_transcript.full_text,
        dialogue=new_transcript.dialogue_json,
        duration_seconds=new_transcript.duration_seconds,
        word_count=new_transcript.word_count,
        audio_url=new_transcript.audio_url,
        created_at=new_transcript.created_at,
    )

@router.get("/{session_id}", response_model=TranscriptResponse)
def get_transcript(session_id: str, db: Session = Depends(get_db)):
    transcript = db.query(Transcript).filter(Transcript.session_id == session_id).first()
    if not transcript:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found for this session")
    
    return TranscriptResponse(
        id=transcript.id,
        session_id=transcript.session_id,
        full_text=transcript.full_text,
        dialogue=transcript.dialogue_json,
        duration_seconds=transcript.duration_seconds,
        word_count=transcript.word_count,
        audio_url=transcript.audio_url,
        created_at=transcript.created_at,
    )
