from fastapi import APIRouter, HTTPException, status, Depends
from app.core.auth import get_current_user
from app.database.database import SessionLocal
from app.database.models import InterviewSession, Question
from app.schemas.question import QuestionCreate
from app.database.models import User
from app.services.question_generator import generate_questions as generate_questions_from_text

router = APIRouter(
    prefix="/v1/questions",
    tags=["questions"]
)


# =========================
# LIST QUESTIONS
# =========================
@router.get("/list")
def list_questions(
    bloom_level: str = None,
    difficulty: str = None,
    user=Depends(get_current_user)
):
    db = SessionLocal()
    query = db.query(Question)

    if bloom_level:
        query = query.filter(Question.bloom_level == bloom_level)

    if difficulty:
        query = query.filter(Question.difficulty == difficulty)

    questions = query.all()
    db.close()

    return {
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "sample_answer": q.sample_answer,
                "bloom_level": q.bloom_level,
                "difficulty": q.difficulty,
                "source_type": q.source_type,
                "topic_tags": q.topic_tags
            }
            for q in questions
        ]
    }


# =========================
# GENERATE QUESTIONS FOR SESSION
# =========================
@router.post("/generate/{session_id}")
def generate_questions(
    session_id: int,
    data: QuestionCreate,
    user: User = Depends(get_current_user)
):
    try:
        db = SessionLocal()

        # validate session
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user.id
        ).first()

        if not session:
            db.close()
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        if session.status != "in_progress":
            db.close()
            raise HTTPException(
                status_code=400,
                detail="Session is not active"
            )

        # generate AI questions
        result = generate_questions_from_text(data, str(user.id))

        stored_questions = []

        for q in result["questions"]:
            new_question = Question(
                question_text=q["question_text"],
                sample_answer="",
                bloom_level=q["bloom_level"],
                difficulty=q["difficulty"],
                source_type="ai_generated",
                topic_tags=q["topic_tags"]
            )

            db.add(new_question)
            db.commit()
            db.refresh(new_question)

            stored_questions.append({
                "id": new_question.id,
                "question_text": new_question.question_text,
                "bloom_level": new_question.bloom_level,
                "difficulty": new_question.difficulty,
                "topic_tags": new_question.topic_tags,
                "estimated_answer_time_sec": q["estimated_answer_time_sec"]
            })

        db.close()

        return {
            "session_id": session_id,
            "questions": stored_questions
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =========================
# GET SINGLE QUESTION
# =========================
@router.get("/get/{question_id}")
def get_question(
    question_id: int,
    user=Depends(get_current_user)
):
    db = SessionLocal()

    question = db.query(Question).filter(
        Question.id == question_id
    ).first()

    db.close()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return {
        "id": question.id,
        "question_text": question.question_text,
        "sample_answer": question.sample_answer,
        "bloom_level": question.bloom_level,
        "difficulty": question.difficulty,
        "source_type": question.source_type,
        "topic_tags": question.topic_tags
    }
