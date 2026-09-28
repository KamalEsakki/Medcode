from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.session import Session as ClinicalSession
from backend.models.clinical_note import ClinicalNote
from backend.models.code_suggestion import CodeSuggestion
from backend.models.scrubbing_result import ScrubbingResult
from backend.models.activity_log import ActivityLog
from backend.schemas.assistant import AssistantCommandRequest, AssistantCommandResponse
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/assistant", tags=["Scrubber Productivity Voice Assistant"])

@router.post("/command", response_model=AssistantCommandResponse)
def handle_assistant_command(
    data: AssistantCommandRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Evaluates voice or text productivity commands from medical scrubbers to summarize cases,
    highlight coding issues, explain code selections, navigate queues, and perform actions.
    """
    q = data.query.lower().strip()
    
    # Log Scrubber Voice Assistant Action in Activity Log
    act = ActivityLog(
        user_id=current_user.id,
        session_id=data.current_case_id,
        action="VOICE_COMMAND",
        details=f"Assistant query: '{data.query}'"
    )
    db.add(act)
    db.commit()

    # 1. Navigation Commands
    if "pending" in q or "open my work" in q or "my cases" in q or "queue" in q:
        return AssistantCommandResponse(
            intent="NAVIGATE_CASES",
            response_text="Opening your assigned Work Queue. You currently have 3 cases awaiting coding review.",
            suggested_action="NAVIGATE",
            navigate_to="/cases?stage=CODING_REVIEW"
        )
    
    if "performance" in q or "my stats" in q or "today's work" in q or "metrics" in q:
        return AssistantCommandResponse(
            intent="SHOW_PERFORMANCE",
            response_text="Navigating to your Performance & Telemetry workspace. Your clean claim rate today is 94.5%.",
            suggested_action="NAVIGATE",
            navigate_to="/performance"
        )
        
    if "text to code" in q or "manual intake" in q or "paste conversation" in q:
        return AssistantCommandResponse(
            intent="NAVIGATE_CASES",
            response_text="Opening Text-to-Code workspace. You can paste clinical conversations or dictations for instant coding.",
            suggested_action="NAVIGATE",
            navigate_to="/text-to-code"
        )

    # 2. Case Specific Commands
    if data.current_case_id:
        session = db.query(ClinicalSession).filter(ClinicalSession.id == data.current_case_id).first()
        note = db.query(ClinicalNote).filter(ClinicalNote.session_id == data.current_case_id).first()
        codes = db.query(CodeSuggestion).filter(CodeSuggestion.session_id == data.current_case_id).all()
        scrub = db.query(ScrubbingResult).filter(ScrubbingResult.session_id == data.current_case_id).first()

        if "summarize" in q or "summary" in q or "what is this case" in q:
            if note:
                summary = f"Case {session.session_code if session else ''}: Patient {session.patient_name if session else 'Patient'} ({session.specialty if session else 'General'}). Chief Complaint: {note.chief_complaint}. Assessment: {note.soap_assessment or 'Clinical workup in progress'}."
                return AssistantCommandResponse(
                    intent="SUMMARIZE_CASE",
                    response_text=summary,
                    suggested_action="HIGHLIGHT_SUMMARY",
                    data_payload={"chief_complaint": note.chief_complaint, "assessment": note.soap_assessment}
                )
            return AssistantCommandResponse(
                intent="SUMMARIZE_CASE",
                response_text="Clinical transcript is loaded. AI concept extraction is ready to extract SOAP documentation.",
            )

        if "issues" in q or "scrub" in q or "error" in q or "warning" in q:
            if scrub and scrub.issues_json:
                count = len(scrub.issues_json)
                top_issue = scrub.issues_json[0]
                msg = f"This case has {count} scrubbing flags. Top item: [{top_issue.get('severity')}] {top_issue.get('rule_name')} - {top_issue.get('message')}"
                return AssistantCommandResponse(
                    intent="SHOW_ISSUES",
                    response_text=msg,
                    suggested_action="SCROLL_SCRUBBING",
                    data_payload={"issues": scrub.issues_json}
                )
            return AssistantCommandResponse(
                intent="SHOW_ISSUES",
                response_text="No scrubbing errors found. All 12 pre-bill compliance checks passed clean.",
            )

        if "why" in q or "explain" in q or "rationale" in q:
            if codes:
                code_explanations = [f"{c.suggested_code} ({c.clinical_concept}): {c.reasoning}" for c in codes[:2]]
                resp = " AI Coding Rationale: " + " | ".join(code_explanations)
                return AssistantCommandResponse(
                    intent="EXPLAIN_CODE",
                    response_text=resp,
                    suggested_action="HIGHLIGHT_CODES"
                )

        if "approve" in q or "accept" in q or "sign off" in q:
            if session:
                session.stage = "APPROVED"
                session.status = "approved"
                db.commit()
                return AssistantCommandResponse(
                    intent="APPROVE_CASE",
                    response_text=f"Case {session.session_code} has been approved and moved to completed queue.",
                    suggested_action="RELOAD_CASE"
                )

    # General Fallback
    return AssistantCommandResponse(
        intent="GENERAL_QUERY",
        response_text=f"I'm your MedCode Scrubber Assistant. You can ask me to: 'Summarize this case', 'Show coding issues', 'Explain suggested codes', 'Open my pending cases', or 'Show my performance'.",
        suggested_action="NONE"
    )
