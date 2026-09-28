from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.models.notification import Notification
from backend.schemas.notification import NotificationCreate, NotificationResponse
from backend.services.auth_service import get_current_user

router = APIRouter(prefix="/notifications", tags=["Work Notifications"])

@router.get("", response_model=List[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all work notifications for the authenticated user.
    """
    notes = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(30).all()
    
    # Auto-seed initial welcome notifications if empty
    if not notes:
        demo_notes = [
            Notification(
                user_id=current_user.id,
                title="New Case Assigned",
                message="Case MC-2026-0891 (Cardiology Teleconsult) has been assigned to your queue.",
                type="CASE_ASSIGNED",
                link_url="/cases",
                is_read=False,
            ),
            Notification(
                user_id=current_user.id,
                title="Claim Scrubbing Warning Flagged",
                message="High-risk cardiac code R07.9 flagged for Medical Necessity check in Case MC-2026-0891.",
                type="SCRUBBING_ERROR",
                link_url="/scrubbing",
                is_read=False,
            ),
            Notification(
                user_id=current_user.id,
                title="AI Transcript Ready",
                message="Audio stream from Zoom consultation converted and ready for clinical concept extraction.",
                type="REVIEW_REQUIRED",
                link_url="/transcripts",
                is_read=True,
            ),
        ]
        for n in demo_notes:
            db.add(n)
        db.commit()
        notes = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()

    return notes

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    note.is_read = True
    db.commit()
    db.refresh(note)
    return note

@router.post("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"success": True, "message": "All notifications marked as read"}
