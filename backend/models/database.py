"""
SQLAlchemy models for Interview Agent MVP.
Based on PRD v1.1 data model design.
"""

import enum
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    create_engine, Column, String, Text, DateTime, Boolean,
    ForeignKey, Integer, Float, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

# --- Enums ---

class FileType(enum.Enum):
    pdf = "pdf"
    docx = "docx"
    image = "image"

class InterviewLevel(enum.Enum):
    daily_intern = "daily_intern"
    summer_intern = "summer_intern"
    campus = "campus"

class InterviewLanguage(enum.Enum):
    chinese = "chinese"
    english = "english"
    mixed = "mixed"

class InterviewRound(enum.Enum):
    first = "first"
    second = "second"
    hr = "hr"

class InterviewerRole(enum.Enum):
    business = "business"
    manager = "manager"
    hr = "hr"

class InterviewerStyle(enum.Enum):
    professional = "professional"
    gentle = "gentle"
    pressure = "pressure"

class SessionStatus(enum.Enum):
    in_progress = "in_progress"
    paused = "paused"
    completed = "completed"

class ProgressStage(enum.Enum):
    applied = "applied"
    screening = "screening"
    test = "test"
    interview = "interview"
    offer = "offer"
    closed = "closed"

class ProgressStatus(enum.Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    withdrawn = "withdrawn"

class ApplicationChannel(enum.Enum):
    official = "official"
    referral = "referral"
    boss = "boss"
    lagou = "lagou"
    maimai = "maimai"
    other = "other"

class Priority(enum.Enum):
    p0 = "p0"
    p1 = "p1"
    p2 = "p2"
    p3 = "p3"


# --- Models ---

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    target_city = Column(String(50), nullable=True)
    career_goal = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_profiles = relationship("JobProfile", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    resume_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False, default="")
    file_type = Column(SQLEnum(FileType), nullable=False)
    raw_text = Column(Text, nullable=True)
    content_json = Column(JSON, nullable=True)
    content_json_ver = Column(Integer, default=1)
    parsed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="resumes")
    interview_sessions = relationship("InterviewSession", back_populates="resume")


class JobProfile(Base):
    __tablename__ = "job_profiles"

    profile_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    target_company = Column(String(100), nullable=False)
    target_position = Column(String(100), nullable=False)
    interview_level = Column(SQLEnum(InterviewLevel), nullable=False)
    position_direction = Column(String(50), nullable=True)
    interview_language = Column(SQLEnum(InterviewLanguage), nullable=False)
    job_description = Column(Text, nullable=False)
    is_reusable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="job_profiles")
    interview_sessions = relationship("InterviewSession", back_populates="job_profile")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("job_profiles.profile_id"), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.resume_id"), nullable=False)
    interview_round = Column(SQLEnum(InterviewRound), nullable=False)
    interviewer_role = Column(SQLEnum(InterviewerRole), nullable=False)
    interviewer_style = Column(SQLEnum(InterviewerStyle), default=InterviewerStyle.professional)
    conversation_history = Column(JSON, nullable=False, default=list)
    summary_at_pause = Column(Text, nullable=True)
    current_question_id = Column(String(36), nullable=True)
    score_json = Column(JSON, nullable=True)
    reflection_summary = Column(Text, nullable=True)
    reflection_notes = Column(JSON, nullable=True)
    starred_questions = Column(JSON, nullable=True)
    is_voice_enabled = Column(Boolean, default=False)
    elapsed_seconds = Column(Integer, default=0)
    status = Column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.in_progress)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interview_sessions")
    job_profile = relationship("JobProfile", back_populates="interview_sessions")
    resume = relationship("Resume", back_populates="interview_sessions")
    questions = relationship(
        "Question",
        back_populates="session",
        cascade="all, delete-orphan",
        primaryjoin="InterviewSession.session_id == Question.session_id",
    )


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    topic = Column(String(100), nullable=True)
    order_index = Column(Integer, nullable=False)
    is_follow_up = Column(Boolean, default=False)
    follow_up_count = Column(Integer, default=0)
    relevance_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("InterviewSession", back_populates="questions", foreign_keys=[session_id])


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    profile_id = Column(String(36), ForeignKey("job_profiles.profile_id"), nullable=True)
    resume_id = Column(String(36), ForeignKey("resumes.resume_id"), nullable=True)
    interview_session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=True)
    company_name = Column(String(100), nullable=False)
    job_title = Column(String(100), nullable=False)
    job_location = Column(String(50), nullable=True)
    progress_stage = Column(SQLEnum(ProgressStage), nullable=False)
    progress_status = Column(SQLEnum(ProgressStatus), nullable=False)
    application_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    job_url = Column(String(500), nullable=True)
    application_channel = Column(SQLEnum(ApplicationChannel), nullable=True)
    priority = Column(SQLEnum(Priority), nullable=True)
    salary_range = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="applications")


# --- Database Engine & Session ---

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/interview_agent.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
