import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.models.user import User
from backend.models.session import Session as ClinicalSession
from backend.models.transcript import Transcript
from backend.models.clinical_note import ClinicalNote
from backend.models.code_suggestion import CodeSuggestion
from backend.models.scrubbing_result import ScrubbingResult
from backend.models.review_audit import ReviewAudit
from backend.models.case_document import CaseDocument
from backend.models.activity_log import ActivityLog
from backend.models.notification import Notification
from backend.services.auth_service import get_password_hash
from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    """
    Seeds initial demonstration users, clinical cases, transcripts, documents, and coding data.
    """
    # 1. Create Demo Users if not present
    existing_user = db.query(User).filter(User.email == "coder@medcode.ai").first()
    if not existing_user:
        logger.info("Seeding demo users...")
        users = [
            User(
                email="coder@medcode.ai",
                hashed_password=get_password_hash("demo123"),
                full_name="Marcus Vance, CPC",
                role="coder",
                employee_id="SCRUB-4409",
                organization="Apex Health RCM Systems",
                department="Inpatient & Outpatient Clinical Coding",
                specialization="Cardiology & Multi-Specialty Scrubbing",
                phone="+1 (555) 234-8901",
                is_active=True,
                last_login=datetime.utcnow(),
            ),
            User(
                email="doctor@medcode.ai",
                hashed_password=get_password_hash("demo123"),
                full_name="Dr. Sarah Lin, MD",
                role="physician",
                employee_id="MD-7812",
                organization="Memorial Regional Health",
                department="Department of Cardiovascular Medicine",
                specialization="Cardiovascular & Internal Medicine",
                phone="+1 (555) 890-1234",
                is_active=True,
                last_login=datetime.utcnow(),
            ),
            User(
                email="auditor@medcode.ai",
                hashed_password=get_password_hash("demo123"),
                full_name="Elena Rostova, RHIA",
                role="auditor",
                employee_id="AUDIT-1092",
                organization="National Compliance & Audit Group",
                department="Regulatory Compliance & Claims Audit",
                specialization="CMS Pre-bill & OIG Compliance",
                phone="+1 (555) 789-4560",
                is_active=True,
                last_login=datetime.utcnow(),
            ),
            User(
                email="demo@medcode.ai",
                hashed_password=get_password_hash("demo123"),
                full_name="Dr. Demo User, MD",
                role="coder",
                employee_id="SCRUB-0001",
                organization="Apex Health RCM Systems",
                department="Clinical Revenue & Coding",
                specialization="General Medical Coding",
                is_active=True,
                last_login=datetime.utcnow(),
            ),
        ]
        for u in users:
            db.add(u)
        db.commit()

    coder_user = db.query(User).filter(User.email == "coder@medcode.ai").first()
    coder_id = coder_user.id if coder_user else None
    coder_name = coder_user.full_name if coder_user else "Marcus Vance, CPC"

    # 2. Check if sessions already exist
    session_count = db.query(ClinicalSession).count()
    if session_count > 0:
        logger.info(f"Database already populated with {session_count} clinical sessions.")
        return

    logger.info("Seeding realistic clinical encounters with complete end-to-end pipeline data...")

    # Scenario 1: Chest Pain / Cardiology (Zoom Consultation)
    sess1 = ClinicalSession(
        session_code="MC-2026-0891",
        patient_name="Robert Davis",
        patient_age=58,
        patient_gender="Male",
        doctor_name="Dr. Sarah Lin, MD",
        specialty="Cardiology",
        session_type="Specialist Telehealth Consultation",
        consultation_source="Zoom",
        priority="URGENT",
        stage="CODING_REVIEW",
        status="completed",
        total_charges=425.00,
        zoom_meeting_url="https://zoom.us/j/9876543210?pwd=clinicalPasscode123",
        zoom_meeting_id="9876543210",
        assigned_scrubber_id=coder_id,
        assigned_scrubber_name=coder_name,
    )
    db.add(sess1)
    db.commit()
    db.refresh(sess1)

    tr_data1 = ai_service.transcribe_audio(scenario_hint="chest_pain")
    tr1 = Transcript(
        session_id=sess1.id,
        full_text=tr_data1["full_text"],
        dialogue_json=tr_data1["dialogue"],
        duration_seconds=145,
        word_count=tr_data1["word_count"],
    )
    db.add(tr1)

    note_data1 = ai_service.extract_clinical_information(tr_data1["full_text"])
    cn1 = ClinicalNote(session_id=sess1.id, **note_data1)
    db.add(cn1)

    codes1 = ai_service.generate_code_suggestions(note_data1)
    for c in codes1:
        cs = CodeSuggestion(session_id=sess1.id, **c)
        db.add(cs)

    scrub_data1 = ai_service.generate_scrubbing_warnings(note_data1, codes1)
    sr1 = ScrubbingResult(
        session_id=sess1.id,
        total_checks=scrub_data1["total_checks"],
        passed_count=scrub_data1["passed_count"],
        warning_count=scrub_data1["warning_count"],
        error_count=scrub_data1["error_count"],
        status=scrub_data1["status"],
        issues_json=scrub_data1["issues"],
    )
    db.add(sr1)

    # Attach Documents & Activity Logs
    doc1 = CaseDocument(
        session_id=sess1.id,
        filename="Clinical_Documentation_MC-2026-0891.pdf",
        file_type="Clinical Note PDF",
        file_size_bytes=38450,
        uploaded_by="MedCode AI Service"
    )
    db.add(doc1)
    
    if coder_id:
        act1 = ActivityLog(
            user_id=coder_id,
            session_id=sess1.id,
            action="OPENED_CASE",
            details="Opened Case MC-2026-0891 (Cardiology Teleconsult) for coding review."
        )
        db.add(act1)

    # Scenario 2: Type 2 Diabetes / Internal Medicine (Microsoft Teams)
    sess2 = ClinicalSession(
        session_code="MC-2026-0892",
        patient_name="Elena Rostova",
        patient_age=64,
        patient_gender="Female",
        doctor_name="Dr. Marcus Vance, MD",
        specialty="Internal Medicine",
        session_type="Chronic Care Review",
        consultation_source="Microsoft Teams",
        priority="HIGH",
        stage="APPROVED",
        status="reviewed",
        total_charges=315.00,
        teams_meeting_url="https://teams.microsoft.com/l/meetup-join/19%3ameeting_diabetic_followup",
        teams_meeting_id="teams-diab-902",
        assigned_scrubber_id=coder_id,
        assigned_scrubber_name=coder_name,
    )
    db.add(sess2)
    db.commit()
    db.refresh(sess2)

    tr_data2 = ai_service.transcribe_audio(scenario_hint="diabetes")
    tr2 = Transcript(
        session_id=sess2.id,
        full_text=tr_data2["full_text"],
        dialogue_json=tr_data2["dialogue"],
        duration_seconds=130,
        word_count=tr_data2["word_count"],
    )
    db.add(tr2)

    note_data2 = ai_service.extract_clinical_information(tr_data2["full_text"])
    cn2 = ClinicalNote(session_id=sess2.id, **note_data2)
    db.add(cn2)

    codes2 = ai_service.generate_code_suggestions(note_data2)
    for c in codes2:
        c_copy = dict(c)
        c_copy["review_status"] = "APPROVED"
        c_copy["reviewed_by"] = coder_name
        c_copy["reviewed_at"] = datetime.utcnow()
        cs = CodeSuggestion(session_id=sess2.id, **c_copy)
        db.add(cs)

    scrub_data2 = ai_service.generate_scrubbing_warnings(note_data2, codes2)
    sr2 = ScrubbingResult(
        session_id=sess2.id,
        total_checks=scrub_data2["total_checks"],
        passed_count=scrub_data2["passed_count"],
        warning_count=scrub_data2["warning_count"],
        error_count=scrub_data2["error_count"],
        status=scrub_data2["status"],
        issues_json=scrub_data2["issues"],
    )
    db.add(sr2)

    doc2 = CaseDocument(
        session_id=sess2.id,
        filename="CMS1500_Claim_Export_MC-2026-0892.edi",
        file_type="EDI 837P Claim Export",
        file_size_bytes=14200,
        uploaded_by="Revenue Cycle Engine"
    )
    db.add(doc2)

    # Scenario 3: Acute Bronchitis / Pulmonology (Manual Text Intake)
    sess3 = ClinicalSession(
        session_code="MC-2026-0893",
        patient_name="David Miller",
        patient_age=34,
        patient_gender="Male",
        doctor_name="Dr. Amy Chen, MD",
        specialty="Pulmonology",
        session_type="Urgent Care Text Intake",
        consultation_source="Manual Text",
        priority="NORMAL",
        stage="SCRUBBING",
        status="analyzed",
        total_charges=260.00,
        assigned_scrubber_id=coder_id,
        assigned_scrubber_name=coder_name,
    )
    db.add(sess3)
    db.commit()
    db.refresh(sess3)

    tr_data3 = ai_service.transcribe_audio(scenario_hint="bronchitis")
    tr3 = Transcript(
        session_id=sess3.id,
        full_text=tr_data3["full_text"],
        dialogue_json=tr_data3["dialogue"],
        duration_seconds=110,
        word_count=tr_data3["word_count"],
    )
    db.add(tr3)

    note_data3 = ai_service.extract_clinical_information(tr_data3["full_text"])
    cn3 = ClinicalNote(session_id=sess3.id, **note_data3)
    db.add(cn3)

    codes3 = ai_service.generate_code_suggestions(note_data3)
    for c in codes3:
        cs = CodeSuggestion(session_id=sess3.id, **c)
        db.add(cs)

    scrub_data3 = ai_service.generate_scrubbing_warnings(note_data3, codes3)
    sr3 = ScrubbingResult(
        session_id=sess3.id,
        total_checks=scrub_data3["total_checks"],
        passed_count=scrub_data3["passed_count"],
        warning_count=scrub_data3["warning_count"],
        error_count=scrub_data3["error_count"],
        status=scrub_data3["status"],
        issues_json=scrub_data3["issues"],
    )
    db.add(sr3)

    # Initial Work Notifications for Coder
    if coder_id:
        notif1 = Notification(
            user_id=coder_id,
            title="Assigned to Urgent Case MC-2026-0891",
            message="Cardiology teleconsultation assigned with high-risk ECG medical necessity flag.",
            type="CASE_ASSIGNED",
            link_url="/cases",
            is_read=False,
        )
        notif2 = Notification(
            user_id=coder_id,
            title="Antimicrobial Stewardship Flag",
            message="Rule RULE-ANTIBIOTIC-003 flagged acute bronchitis documentation for Case MC-2026-0893.",
            type="SCRUBBING_ERROR",
            link_url="/scrubbing",
            is_read=False,
        )
        db.add(notif1)
        db.add(notif2)

    db.commit()
    logger.info("Database seed completed successfully with professional medical cases.")
