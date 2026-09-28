import random
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.database import get_db
from backend.models.session import Session as ClinicalSession
from backend.models.code_suggestion import CodeSuggestion
from backend.models.scrubbing_result import ScrubbingResult
from backend.models.transcript import Transcript
from backend.models.clinical_note import ClinicalNote
from backend.models.case_document import CaseDocument
from backend.models.activity_log import ActivityLog
from backend.models.user import User
from backend.schemas.session import SessionCreate, SessionUpdate, SessionResponse, TextToCodeRequest, CaseStageUpdateRequest
from backend.schemas.case_document import CaseDocumentCreate, CaseDocumentResponse
from backend.services.auth_service import get_current_user
from backend.services.ai_service import ai_service

router = APIRouter(prefix="/sessions", tags=["Clinical Sessions & Case Management"])

def format_session_response(session: ClinicalSession, db: Session) -> SessionResponse:
    code_count = db.query(CodeSuggestion).filter(CodeSuggestion.session_id == session.id).count()
    scrub_result = db.query(ScrubbingResult).filter(ScrubbingResult.session_id == session.id).first()
    scrub_status = scrub_result.status if scrub_result else "PASS"
    doc_count = db.query(CaseDocument).filter(CaseDocument.session_id == session.id).count()
    
    return SessionResponse(
        id=session.id,
        session_code=session.session_code,
        patient_name=session.patient_name,
        patient_age=session.patient_age,
        patient_gender=session.patient_gender,
        doctor_name=session.doctor_name,
        specialty=session.specialty,
        session_type=session.session_type,
        status=session.status,
        stage=getattr(session, "stage", "NEW") or "NEW",
        priority=getattr(session, "priority", "NORMAL") or "NORMAL",
        consultation_source=getattr(session, "consultation_source", "Zoom") or "Zoom",
        total_charges=getattr(session, "total_charges", 320.00) or 320.00,
        assigned_scrubber_id=getattr(session, "assigned_scrubber_id", None),
        assigned_scrubber_name=getattr(session, "assigned_scrubber_name", None),
        zoom_meeting_url=getattr(session, "zoom_meeting_url", None),
        zoom_meeting_id=getattr(session, "zoom_meeting_id", None),
        teams_meeting_url=getattr(session, "teams_meeting_url", None),
        teams_meeting_id=getattr(session, "teams_meeting_id", None),
        created_at=session.created_at,
        updated_at=session.updated_at,
        transcript_count=1 if session.transcript else 0,
        code_count=code_count,
        scrubbing_status=scrub_status,
        document_count=doc_count,
    )

@router.get("", response_model=List[SessionResponse])
def list_sessions(
    stage: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ClinicalSession)
    if stage and stage != "ALL":
        query = query.filter(ClinicalSession.stage == stage)
    if priority and priority != "ALL":
        query = query.filter(ClinicalSession.priority == priority)
    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            ClinicalSession.patient_name.ilike(s),
            ClinicalSession.session_code.ilike(s),
            ClinicalSession.specialty.ilike(s),
            ClinicalSession.doctor_name.ilike(s),
        ))
    sessions = query.order_by(ClinicalSession.created_at.desc()).all()
    return [format_session_response(s, db) for s in sessions]

@router.get("/my-cases", response_model=List[SessionResponse])
def list_my_cases(
    stage: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns cases assigned to or authorized for the authenticated scrubber/coder.
    Enforces user data isolation.
    """
    query = db.query(ClinicalSession)
    
    # Scrubber sees their assigned cases or created cases; Admin/Auditor sees all
    if current_user.role not in ["admin", "auditor"]:
        query = query.filter(
            or_(
                ClinicalSession.assigned_scrubber_id == current_user.id,
                ClinicalSession.user_id == current_user.id,
                ClinicalSession.assigned_scrubber_id.is_(None) # Unassigned open queue cases
            )
        )
    
    if stage and stage != "ALL":
        query = query.filter(ClinicalSession.stage == stage)
    if priority and priority != "ALL":
        query = query.filter(ClinicalSession.priority == priority)
    if search:
        s = f"%{search}%"
        query = query.filter(or_(
            ClinicalSession.patient_name.ilike(s),
            ClinicalSession.session_code.ilike(s),
            ClinicalSession.specialty.ilike(s),
            ClinicalSession.doctor_name.ilike(s),
        ))
        
    sessions = query.order_by(ClinicalSession.created_at.desc()).all()
    return [format_session_response(s, db) for s in sessions]

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        
    # Check data isolation
    if current_user and current_user.role not in ["admin", "auditor"]:
        if session.assigned_scrubber_id and session.assigned_scrubber_id != current_user.id and session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access Denied: You do not have authorization to view encounters assigned to another scrubber."
            )

    return format_session_response(session, db)

@router.post("", response_model=SessionResponse)
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    code_num = random.randint(1000, 9999)
    session_code = f"MC-2026-{code_num}"
    
    new_session = ClinicalSession(
        session_code=session_code,
        patient_name=data.patient_name,
        patient_age=data.patient_age,
        patient_gender=data.patient_gender,
        doctor_name=data.doctor_name,
        specialty=data.specialty,
        session_type=data.session_type,
        consultation_source=data.consultation_source or "Zoom",
        priority=data.priority or "NORMAL",
        stage=data.stage or "NEW",
        total_charges=data.total_charges or 320.00,
        status="recording",
        zoom_meeting_url=data.zoom_meeting_url,
        zoom_meeting_id=data.zoom_meeting_id,
        teams_meeting_url=data.teams_meeting_url,
        teams_meeting_id=data.teams_meeting_id,
        user_id=current_user.id if current_user else None,
        assigned_scrubber_id=data.assigned_scrubber_id or (current_user.id if current_user else None),
        assigned_scrubber_name=data.assigned_scrubber_name or (current_user.full_name if current_user else "Assigned Scrubber"),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Log creation activity
    if current_user:
        act = ActivityLog(
            user_id=current_user.id,
            session_id=new_session.id,
            action="OPENED_CASE",
            details=f"Created Case {session_code} for {data.patient_name}"
        )
        db.add(act)
        db.commit()

    return format_session_response(new_session, db)

@router.post("/text-to-code", response_model=SessionResponse)
def create_text_to_code_case(
    data: TextToCodeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Direct Text-to-Code Intake: Creates a case from raw clinical text / dictation,
    extracts clinical SOAP findings, generates ICD-10/CPT codes, runs claim scrubbing,
    and returns the fully processed case ready for scrubber review.
    """
    code_num = random.randint(1000, 9999)
    session_code = f"MC-TXT-{code_num}"
    
    # 1. Create Session
    session = ClinicalSession(
        session_code=session_code,
        patient_name=data.patient_name or "Clinical Walk-in Encounter",
        patient_age=data.patient_age or 52,
        patient_gender=data.patient_gender or "Female",
        doctor_name=data.doctor_name or (current_user.full_name if current_user else "Dr. Sarah Lin, MD"),
        specialty=data.specialty or "General Practice",
        session_type=data.session_type or "Direct Text Intake",
        consultation_source="Manual Text",
        priority=data.priority or "NORMAL",
        stage="CODING_REVIEW",
        status="analyzed",
        total_charges=385.00,
        user_id=current_user.id if current_user else None,
        assigned_scrubber_id=current_user.id if current_user else None,
        assigned_scrubber_name=current_user.full_name if current_user else "Lead Medical Scrubber",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 2. Attach Transcript
    lines = [line.strip() for line in data.clinical_text.strip().split("\n") if line.strip()]
    dialogue_list = []
    for i, l in enumerate(lines):
        speaker = "Doctor" if i % 2 == 0 else "Patient"
        if ":" in l and l.split(":")[0].strip().lower() in ["doctor", "dr", "dr.", "physician"]:
            speaker = "Doctor"
            l = l.split(":", 1)[1].strip()
        elif ":" in l and l.split(":")[0].strip().lower() in ["patient", "pt"]:
            speaker = "Patient"
            l = l.split(":", 1)[1].strip()
            
        dialogue_list.append({
            "speaker": speaker,
            "text": l,
            "timestamp": f"00:{i*12:02d}",
            "consultationId": session.id,
        })
    
    tr = Transcript(
        session_id=session.id,
        full_text=data.clinical_text,
        dialogue_json=dialogue_list,
        duration_seconds=len(lines) * 15,
        word_count=len(data.clinical_text.split()),
    )
    db.add(tr)
    db.commit()

    # 3. Clinical Extraction
    note_dict = ai_service.extract_clinical_information(data.clinical_text)
    cn = ClinicalNote(session_id=session.id, **note_dict)
    db.add(cn)

    # 4. Code Suggestions
    code_list = ai_service.generate_code_suggestions(note_dict)
    for c in code_list:
        cs = CodeSuggestion(session_id=session.id, **c)
        db.add(cs)

    # 5. Claim Scrubbing
    scrub_dict = ai_service.generate_scrubbing_warnings(note_dict, code_list)
    sr = ScrubbingResult(
        session_id=session.id,
        total_checks=scrub_dict["total_checks"],
        passed_count=scrub_dict["passed_count"],
        warning_count=scrub_dict["warning_count"],
        error_count=scrub_dict["error_count"],
        status=scrub_dict["status"],
        issues_json=scrub_dict["issues"],
    )
    db.add(sr)
    
    # 6. Initial Case Document (CMS-1500 Summary)
    doc = CaseDocument(
        session_id=session.id,
        filename=f"Encounter_Summary_{session_code}.pdf",
        file_type="Clinical Summary PDF",
        file_size_bytes=24580,
        uploaded_by="AI Pipeline Engine"
    )
    db.add(doc)

    # 7. Activity Log
    if current_user:
        act = ActivityLog(
            user_id=current_user.id,
            session_id=session.id,
            action="ANALYZED_TRANSCRIPT",
            details=f"Text-to-Code generated {len(code_list)} candidate codes for {session_code}"
        )
        db.add(act)

    db.commit()
    db.refresh(session)
    return format_session_response(session, db)

@router.put("/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, data: SessionUpdate, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(session, key, value)
    
    db.commit()
    db.refresh(session)
    return format_session_response(session, db)

@router.put("/{session_id}/stage", response_model=SessionResponse)
def update_case_stage(
    session_id: str,
    data: CaseStageUpdateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
        
    # Check authorization
    if current_user and current_user.role not in ["admin", "auditor"]:
        if session.assigned_scrubber_id and session.assigned_scrubber_id != current_user.id and session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access Denied: You cannot modify cases assigned to another scrubber."
            )

    # Validate approval prerequisites
    approval_stages = ["APPROVED", "COMPLETED", "READY_FOR_BILLING", "SUBMITTED", "CLAIM_CLEARED"]
    return_stages = ["RETURNED", "RETURNED_TO_PHYSICIAN", "QUERY_PROVIDER"]

    if data.stage.upper() in approval_stages:
        scrub = db.query(ScrubbingResult).filter(ScrubbingResult.session_id == session.id).first()
        if scrub and scrub.error_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve claim for billing: {scrub.error_count} blocking claim scrubbing error(s) must be resolved first."
            )
            
        session.status = "approved"
        session.stage = data.stage.upper()
        action_name = "CASE_APPROVED"
        action_detail = f"Approved case {session.session_code} for clean claim transmission. Reviewer note: {data.note or 'Verified by Certified Scrubber'}"
    elif data.stage.upper() in return_stages:
        session.status = "returned"
        session.stage = "RETURNED"
        action_name = "CASE_RETURNED"
        action_detail = f"Returned case {session.session_code} to provider. Reason: {data.note or 'Documentation / Coding correction needed'}"
    else:
        session.stage = data.stage
        action_name = f"STAGE_{data.stage}"
        action_detail = f"Moved case {session.session_code} to stage {data.stage}. Note: {data.note or 'Workflow update'}"
        
    db.commit()
    
    if current_user:
        act = ActivityLog(
            user_id=current_user.id,
            session_id=session.id,
            action=action_name,
            details=action_detail
        )
        db.add(act)
        db.commit()

    db.refresh(session)
    return format_session_response(session, db)

# Case Documents Endpoints
@router.get("/{session_id}/documents", response_model=List[CaseDocumentResponse])
def get_case_documents(session_id: str, db: Session = Depends(get_db)):
    docs = db.query(CaseDocument).filter(CaseDocument.session_id == session_id).all()
    if not docs:
        # Auto-create sample case documents for demo
        session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
        code = session.session_code if session else "MC-2026"
        sample_docs = [
            CaseDocument(
                session_id=session_id,
                filename=f"Clinical_SOAP_Documentation_{code}.pdf",
                file_type="Clinical Note PDF",
                file_size_bytes=34280,
                uploaded_by="Medical Scrubber AI"
            ),
            CaseDocument(
                session_id=session_id,
                filename=f"CMS1500_EDI_837P_Claim_{code}.edi",
                file_type="EDI 837P Claim Export",
                file_size_bytes=12840,
                uploaded_by="Revenue Cycle Engine"
            ),
            CaseDocument(
                session_id=session_id,
                filename=f"Speech_Transcript_{code}.txt",
                file_type="Audio Transcript Export",
                file_size_bytes=8940,
                uploaded_by="Audio Transcription Connector"
            )
        ]
        for d in sample_docs:
            db.add(d)
        db.commit()
        docs = db.query(CaseDocument).filter(CaseDocument.session_id == session_id).all()
    return docs

@router.post("/{session_id}/documents", response_model=CaseDocumentResponse)
def add_case_document(
    session_id: str,
    data: CaseDocumentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    doc = CaseDocument(
        session_id=session_id,
        filename=data.filename,
        file_type=data.file_type,
        file_size_bytes=data.file_size_bytes,
        uploaded_by=current_user.full_name if current_user else "Medical Scrubber"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ClinicalSession).filter(ClinicalSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    db.delete(session)
    db.commit()
    return {"success": True, "message": f"Case {session_id} deleted successfully"}
