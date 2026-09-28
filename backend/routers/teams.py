import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.session import Session as ClinicalSession
from backend.models.transcript import Transcript
from backend.models.user import User
from backend.schemas.zoom import ZoomValidateRequest, ZoomValidateResponse, ZoomJoinRequest, ZoomStatusResponse
from backend.services.teams_service import teams_service
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/teams", tags=["Microsoft Teams Consultation Integration"])

@router.post("/validate", response_model=ZoomValidateResponse)
def validate_teams_url(data: ZoomValidateRequest):
    """
    Validates a Microsoft Teams meeting URL format and extracts meeting ID.
    """
    is_valid, meeting_id, tid, normalized_url, msg = teams_service.validate_teams_url(data.meeting_url)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    return ZoomValidateResponse(
        is_valid=True,
        meeting_id=meeting_id,
        passcode=tid,
        normalized_url=normalized_url,
        message=msg
    )

@router.post("/join", response_model=ZoomStatusResponse)
def join_teams_consultation(
    data: ZoomJoinRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Validates Teams URL, initializes consultation case, loads permitted/demo transcript stream,
    and returns the session with connection status and provenance metadata.
    """
    is_valid, meeting_id, tid, normalized_url, msg = teams_service.validate_teams_url(data.meeting_url)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    is_demo, provenance = teams_service.get_provenance_banner()
    
    code_num = random.randint(1000, 9999)
    session_code = f"MC-MS-{code_num}"
    
    patient_name = data.patient_name or "Demo Patient (Elena Rostova)"
    doctor_name = data.doctor_name or "Dr. Sarah Lin, MD"
    specialty = data.specialty or "Cardiology"
    
    session = ClinicalSession(
        session_code=session_code,
        patient_name=patient_name,
        patient_age=data.patient_age or 64,
        patient_gender=data.patient_gender or "Female",
        doctor_name=doctor_name,
        specialty=specialty,
        session_type=data.session_type or "Microsoft Teams Telehealth Consultation",
        consultation_source="Microsoft Teams",
        status="recording",
        stage="NEW",
        priority="HIGH",
        teams_meeting_url=normalized_url or data.meeting_url,
        teams_meeting_id=meeting_id,
        user_id=current_user.id if current_user else None,
        assigned_scrubber_id=current_user.id if current_user else None,
        assigned_scrubber_name=current_user.full_name if current_user else "Assigned Scrubber",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Attach initial transcript utterances
    dialogue_list = teams_service.get_dialogue_for_consultation(specialty, session.id)
    full_text = "\n\n".join([f"{d['speaker']}: {d['text']}" for d in dialogue_list])
    
    transcript = Transcript(
        session_id=session.id,
        full_text=full_text,
        dialogue_json=dialogue_list,
        duration_seconds=180,
        word_count=len(full_text.split()),
    )
    db.add(transcript)
    db.commit()

    return ZoomStatusResponse(
        session_id=session.id,
        session_code=session.session_code,
        zoom_meeting_id=meeting_id,
        zoom_meeting_url=session.teams_meeting_url,
        connection_status="CONNECTED",
        audio_status="STREAMING",
        transcript_status="STREAMING",
        is_demo_mode=is_demo,
        provenance_label=provenance,
        patient_name=session.patient_name,
        doctor_name=session.doctor_name,
        specialty=session.specialty,
    )
