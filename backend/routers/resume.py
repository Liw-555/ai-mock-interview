"""
Resume upload and parse API.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, Resume, FileType
from services.resume_parser import parse_resume_file

router = APIRouter()

UPLOAD_DIR = "D:/CodeBuddy学习/组会学习/实习Agent-v2/interview-agent/data/uploads"


class ResumeOut(BaseModel):
    resume_id: str
    file_path: str
    original_filename: str
    file_type: str
    parsed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeDetailOut(ResumeOut):
    raw_text: str | None
    content_json: dict | None
    content_json_ver: int


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload resume file (PDF or Word)."""
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext == ".pdf":
        file_type = FileType.pdf
    elif ext == ".docx":
        file_type = FileType.docx
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Only PDF and DOCX are allowed.")

    # Save file
    resume_id = str(uuid.uuid4())
    file_name = f"{resume_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Parse resume
    try:
        raw_text, content_json = parse_resume_file(file_path, file_type)
        parsed_at = datetime.now(timezone.utc)
    except Exception as e:
        # Parsing failed, save raw file but mark as unparsed
        raw_text = None
        content_json = None
        parsed_at = None

    # Create DB record (using a default user for MVP single-user mode)
    from models.database import User
    user = db.query(User).first()
    if not user:
        user = User(user_id=str(uuid.uuid4()), name="Default User")
        db.add(user)
        db.commit()

    resume = Resume(
        resume_id=resume_id,
        user_id=user.user_id,
        file_path=file_path,
        original_filename=file.filename,
        file_type=file_type,
        raw_text=raw_text,
        content_json=content_json,
        content_json_ver=1,
        parsed_at=parsed_at,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


@router.get("", response_model=List[ResumeOut])
async def list_resumes(db: Session = Depends(get_db)):
    """List all uploaded resumes."""
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetailOut)
async def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Get resume details including parsed content."""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Delete a resume."""
    resume = db.query(Resume).filter(Resume.resume_id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Check for linked interview sessions
    from models.database import InterviewSession
    linked_sessions = db.query(InterviewSession).filter(InterviewSession.resume_id == resume_id).count()
    if linked_sessions > 0:
        raise HTTPException(
            status_code=409,
            detail=f"该简历关联了 {linked_sessions} 场面试记录，请先删除相关面试记录"
        )

    # Delete file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}
