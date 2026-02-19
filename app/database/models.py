from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    JSON,
    Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base


# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), default="student")
    auth_provider = Column(String(20), default="email")
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    sessions = relationship("InterviewSession", back_populates="user")


# =========================
# SUBJECTS
# =========================
class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="subject")


# =========================
# QUESTIONS
# =========================
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    sample_answer = Column(Text, nullable=False)
    bloom_level = Column(String(5), nullable=False)
    difficulty = Column(String(10), nullable=False)
    source_type = Column(String(20), nullable=False)
    topic_tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answer", back_populates="question")


# =========================
# INTERVIEW SESSIONS
# =========================
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    mode = Column(String(20), nullable=False)
    bloom_strategy = Column(String(20), default="fixed")
    status = Column(String(20), nullable=False)

    llm_metadata = Column(JSON, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
    subject = relationship("Subject", back_populates="sessions")
    answers = relationship("Answer", back_populates="session")


# =========================
# ANSWERS
# =========================
class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("interview_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))

    answer_text = Column(Text, nullable=False)
    evaluation_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")
