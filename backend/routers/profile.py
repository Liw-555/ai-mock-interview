"""
Job profile API.
"""

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, JobProfile, InterviewLevel, InterviewLanguage, User

router = APIRouter()


class ProfileCreate(BaseModel):
    target_company: str
    target_position: str
    interview_level: str = "daily_intern"
    interview_language: str = "chinese"
    job_description: str


class ProfileUpdate(BaseModel):
    target_company: str | None = None
    target_position: str | None = None
    interview_level: str | None = None
    interview_language: str | None = None
    job_description: str | None = None


class ProfileOut(BaseModel):
    profile_id: str
    target_company: str
    target_position: str
    interview_level: str
    interview_language: str
    job_description: str
    is_reusable: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=ProfileOut)
async def create_profile(data: ProfileCreate, db: Session = Depends(get_db)):
    """Create a new job profile."""
    level_map = {
        "daily_intern": InterviewLevel.daily_intern,
        "summer_intern": InterviewLevel.summer_intern,
        "campus": InterviewLevel.campus,
    }
    lang_map = {
        "chinese": InterviewLanguage.chinese,
        "english": InterviewLanguage.english,
        "mixed": InterviewLanguage.mixed,
    }

    # Get or create default user
    user = db.query(User).first()
    if not user:
        user = User(user_id=str(uuid.uuid4()), name="Default User")
        db.add(user)
        db.commit()

    profile = JobProfile(
        profile_id=str(uuid.uuid4()),
        user_id=user.user_id,
        target_company=data.target_company,
        target_position=data.target_position,
        interview_level=level_map.get(data.interview_level, InterviewLevel.daily_intern),
        interview_language=lang_map.get(data.interview_language, InterviewLanguage.chinese),
        job_description=data.job_description,
        is_reusable=True,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=List[ProfileOut])
async def list_profiles(db: Session = Depends(get_db)):
    """List all job profiles."""
    profiles = db.query(JobProfile).order_by(JobProfile.created_at.desc()).all()
    return profiles


@router.get("/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a job profile by ID."""
    profile = db.query(JobProfile).filter(JobProfile.profile_id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{profile_id}", response_model=ProfileOut)
async def update_profile(profile_id: str, data: ProfileUpdate, db: Session = Depends(get_db)):
    """Update a job profile."""
    profile = db.query(JobProfile).filter(JobProfile.profile_id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    level_map = {
        "daily_intern": InterviewLevel.daily_intern,
        "summer_intern": InterviewLevel.summer_intern,
        "campus": InterviewLevel.campus,
    }
    lang_map = {
        "chinese": InterviewLanguage.chinese,
        "english": InterviewLanguage.english,
        "mixed": InterviewLanguage.mixed,
    }

    if data.target_company is not None:
        profile.target_company = data.target_company
    if data.target_position is not None:
        profile.target_position = data.target_position
    if data.interview_level is not None:
        profile.interview_level = level_map.get(data.interview_level, profile.interview_level)
    if data.interview_language is not None:
        profile.interview_language = lang_map.get(data.interview_language, profile.interview_language)
    if data.job_description is not None:
        profile.job_description = data.job_description

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str, db: Session = Depends(get_db)):
    """Delete a job profile."""
    profile = db.query(JobProfile).filter(JobProfile.profile_id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check for linked interview sessions
    from models.database import InterviewSession
    linked_sessions = db.query(InterviewSession).filter(InterviewSession.profile_id == profile_id).count()
    if linked_sessions > 0:
        raise HTTPException(
            status_code=409,
            detail=f"该岗位资料关联了 {linked_sessions} 场面试记录，请先删除相关面试记录"
        )

    db.delete(profile)
    db.commit()
    return {"message": "Profile deleted successfully"}
