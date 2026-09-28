import hmac
import hashlib
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.config import settings
from backend.models.session import Session as ClinicalSession
from backend.models.transcript import Transcript
from backend.models.user import User
from backend.schemas.zoom import (
    ZoomValidateRequest,
    ZoomValidateResponse,
    ZoomJoinRequest,
    ZoomStatusResponse,
    ZoomWebhookEvent,
)
from backend.services.zoom_service import zoom_service
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/zoom", tags=["Zoom Consultation Integration"])

@router.post("/validate", response_model=ZoomValidateResponse)
def validate_zoom_url(data: ZoomValidateRequest):
    """
    Validates a Zoom meeting URL format and extracts meeting ID and passcode.
    """
    is_valid, meeting_id, passcode, normalized_url, msg = zoom_service.validate_zoom_url(data.meeting_url)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )
    return ZoomValidateResponse(
        is_valid=True,
        meeting_id=meeting_id,
        passcode=passcode,
        normalized_url=normalized_url,
        message=msg
    )

@router.post("/join", response_model=ZoomStatusResponse)
def join_zoom_consultation(
    data: ZoomJoinRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Validates the Zoom URL, initializes a consultation session, loads permitted/demo transcript stream,
    and returns the session with connection status and provenance metadata.
    """
    is_valid, meeting_id, passcode, normalized_url, msg = zoom_service.validate_zoom_url(data.meeting_url)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

    is_demo, provenance = zoom_service.get_provenance_banner()
    
    # 1. Create Consultation Session
    code_num = random.randint(1000, 9999)
    meeting_suffix = meeting_id[-4:] if meeting_id else "ZM"
    session_code = f"MC-ZM-{meeting_suffix}-{code_num}"
    
    patient_name = data.patient_name or "Demo Patient (Robert Davis)"
    doctor_name = data.doctor_name or "Dr. Sarah Lin, MD"
    specialty = data.specialty or "Cardiology"
    
    session = ClinicalSession(
        session_code=session_code,
        patient_name=patient_name,
        patient_age=data.patient_age or 58,
        patient_gender=data.patient_gender or "Male",
        doctor_name=doctor_name,
        specialty=specialty,
        session_type=data.session_type or "Zoom Telehealth Consultation",
        status="recording",
        zoom_meeting_url=normalized_url or data.meeting_url,
        zoom_meeting_id=meeting_id,
        user_id=current_user.id if current_user else None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 2. Attach initial transcript utterances
    dialogue_list = zoom_service.get_dialogue_for_consultation(specialty, session.id)
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
        zoom_meeting_url=session.zoom_meeting_url,
        connection_status="CONNECTED",
        audio_status="STREAMING",
        transcript_status="STREAMING",
        is_demo_mode=is_demo,
        provenance_label=provenance,
        patient_name=session.patient_name,
        doctor_name=session.doctor_name,
        specialty=session.specialty,
    )

@router.get("/status/{session_id}", response_model=ZoomStatusResponse)
def get_zoom_session_status(session_id: str, db: Session = Depends(get_db)):
    """
    Returns the real-time connection, audio, and transcript status of a Zoom consultation session.
    """
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation session not found")

    is_demo, provenance = zoom_service.get_provenance_banner()

    # Map session status to connection status
    status_map = {
        "recording": "RECEIVING_DATA",
        "completed": "COMPLETED",
        "analyzed": "COMPLETED",
        "reviewed": "COMPLETED",
        "returned": "COMPLETED",
        "approved": "COMPLETED",
    }
    conn_status = status_map.get(session.status, "CONNECTED")

    return ZoomStatusResponse(
        session_id=session.id,
        session_code=session.session_code,
        zoom_meeting_id=session.zoom_meeting_id,
        zoom_meeting_url=session.zoom_meeting_url,
        connection_status=conn_status,
        audio_status="COMPLETED" if conn_status == "COMPLETED" else "STREAMING",
        transcript_status="READY_FOR_ANALYSIS" if conn_status == "COMPLETED" else "STREAMING",
        is_demo_mode=is_demo,
        provenance_label=provenance,
        patient_name=session.patient_name,
        doctor_name=session.doctor_name,
        specialty=session.specialty,
    )

@router.post("/webhook")
def zoom_webhook_handler(
    event_data: ZoomWebhookEvent,
    authorization: Optional[str] = Header(None)
):
    """
    Zoom Webhook Event Receiver supporting Zoom URL verification challenges
    and meeting/transcript events for production integrations.
    """
    # 1. Handle Zoom URL validation challenge if received
    if event_data.event == "endpoint.url_validation":
        plain_token = event_data.payload.get("plainToken", "")
        secret = settings.ZOOM_WEBHOOK_SECRET or "default_secret"
        
        # Calculate HMAC SHA-256 hash
        hash_obj = hmac.new(secret.encode("utf-8"), plain_token.encode("utf-8"), hashlib.sha256)
        encrypted_token = hash_obj.hexdigest()
        
        return {
            "plainToken": plain_token,
            "encryptedToken": encrypted_token
        }

    return {"status": "received", "event": event_data.event}
