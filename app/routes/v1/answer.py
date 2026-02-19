from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.database.models import Answer, Question, InterviewSession
from app.database.database import SessionLocal
from app.services.check_answers import check_answer_correctness

router = APIRouter(
    prefix="/v1/answers",
    tags=["answers"]
)


# =========================
# SUBMIT ANSWER
# =========================
@router.post("/submit")
def submit_answer(
    session_id: int,
    question_id: int,
    answer: str,
    user=Depends(get_current_user)
):
    db = SessionLocal()

    # Validate session ownership
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    if session.status != "in_progress":
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not active"
        )

    # Validate question
    question = db.query(Question).filter(
        Question.id == question_id
    ).first()

    if not question:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Evaluate answer
    result = check_answer_correctness(
        question.question_text,
        answer,
        student_id=str(user.id)
    )

    # Save answer
    new_answer = Answer(
        session_id=session.id,
        question_id=question_id,
        answer_text=answer,
        evaluation_score=result["score"],
        feedback=result["feedback"],
        ai_metadata={
            "level": result["level"],
            "explanation": result["explanation"]
        }
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    db.close()

    return {
        "message": "Answer submitted successfully",
        "score": result["score"],
        "feedback": result["feedback"],
        "explanation": result["explanation"],
        "level": result["level"]
    }


# =========================
# GET SESSION HISTORY
# =========================
@router.get("/history/{session_id}")
def get_answer_history(session_id: int, user=Depends(get_current_user)):
    db = SessionLocal()

    # Validate session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    answers = db.query(Answer).filter(
        Answer.session_id == session.id
    ).all()

    history = []

    for ans in answers:
        question = db.query(Question).filter(
            Question.id == ans.question_id
        ).first()

        history.append({
            "answer_id": ans.id,
            "question_id": ans.question_id,
            "question": question.question_text if question else "Question not found",
            "answer": ans.answer_text,
            "score": ans.evaluation_score,
            "feedback": ans.feedback,
            "level": ans.ai_metadata.get("level") if ans.ai_metadata else None,
            "submitted_at": ans.recorded_at
        })

    db.close()

    return {
        "history": history
    }


# =========================
# GET SINGLE ANSWER
# =========================
@router.get("/get/{answer_id}")
def get_answer(answer_id: int, user=Depends(get_current_user)):
    db = SessionLocal()

    answer = db.query(Answer).filter(
        Answer.id == answer_id
    ).first()

    if not answer:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )

    # Validate ownership via session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == answer.session_id,
        InterviewSession.user_id == user.id
    ).first()

    if not session:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    question = db.query(Question).filter(
        Question.id == answer.question_id
    ).first()

    db.close()

    return {
        "answer_id": answer.id,
        "question": question.question_text if question else "Question not found",
        "answer": answer.answer_text,
        "score": answer.evaluation_score,
        "feedback": answer.feedback,
        "level": answer.ai_metadata.get("level") if answer.ai_metadata else None,
        "submitted_at": answer.recorded_at
    }
