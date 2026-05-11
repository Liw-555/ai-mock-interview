"""
Question record API.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, Question

router = APIRouter()


class QuestionOut(BaseModel):
    question_id: str
    session_id: str
    question_text: str
    topic: str | None
    order_index: int
    is_follow_up: bool
    follow_up_count: int
    relevance_score: float | None

    class Config:
        from_attributes = True


@router.get("/session/{session_id}", response_model=List[QuestionOut])
async def list_questions(session_id: str, db: Session = Depends(get_db)):
    """List all questions for a session."""
    questions = db.query(Question).filter(Question.session_id == session_id).order_by(Question.order_index).all()
    return questions


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: str, db: Session = Depends(get_db)):
    """Get a single question."""
    question = db.query(Question).filter(Question.question_id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
