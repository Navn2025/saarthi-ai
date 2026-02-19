from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from app.core.auth import get_current_user
from app.database.models import InterviewSession, Subject
from app.database.database import SessionLocal
from app.database.models import User

router = APIRouter(
    prefix="/v1/interview_sessions",
    tags=["interview_sessions"]
)


# =========================
# START SESSION
# =========================
@router.post("/start")
def start_session(
    subject: str,
    mode: str,
    user: User = Depends(get_current_user)
):
    db = SessionLocal()

    # Get or create subject
    subject_obj = db.query(Subject).filter(
        Subject.name == subject
    ).first()

    if not subject_obj:
        subject_obj = Subject(
            name=subject,
            description=f"{subject} subject"
        )
        db.add(subject_obj)
        db.commit()
        db.refresh(subject_obj)

    # Create session
    session = InterviewSession(
        user_id=user.id,
        subject_id=subject_obj.id,
        mode=mode,
        bloom_strategy="fixed",
        status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    db.close()

    return {
        "message": "Session started",
        "session_id": session.id,
        "subject": subject,
        "mode": mode,
        "status": session.status,
        "started_at": session.started_at
    }


# =========================
# LIST USER SESSIONS
# =========================
@router.get("/list")
def list_interview_sessions(user=Depends(get_current_user)):
    db = SessionLocal()

    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user.id
    ).all()

    db.close()

    return {
        "interview_sessions": [
            {
                "id": s.id,
                "subject_id": s.subject_id,
                "mode": s.mode,
                "status": s.status,
                "started_at": s.started_at,
                "ended_at": s.ended_at
            }
            for s in sessions
        ]
    }


# =========================
# GET SINGLE SESSION
# =========================
@router.get("/get/{session_id}")
def get_interview_session(
    session_id: int,
    user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    db.close()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    return {
        "id": session.id,
        "subject_id": session.subject_id,
        "mode": session.mode,
        "status": session.status,
        "started_at": session.started_at,
        "ended_at": session.ended_at
    }


# =========================
# END SESSION
# =========================
@router.post("/end/{session_id}")
def end_interview_session(
    session_id: int,
    user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    if session.status == "completed":
        db.close()
        return {
            "message": "Session already completed",
            "session_id": session.id
        }

    session.status = "completed"
    session.ended_at = datetime.utcnow()

    db.commit()
    db.refresh(session)
    db.close()

    return {
        "message": "Interview session ended successfully",
        "session_id": session.id,
        "status": session.status,
        "ended_at": session.ended_at
    }


# =========================
# DELETE SESSION (OPTIONAL)
# =========================
@router.delete("/delete/{session_id}")
def delete_interview_session(
    session_id: int,
    user=Depends(get_current_user)
):
    db = SessionLocal()

    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    db.delete(session)
    db.commit()
    db.close()

    return {"message": "Interview session deleted successfully"}
