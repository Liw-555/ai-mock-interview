"""
Evaluation report API.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, InterviewSession, JobProfile

router = APIRouter()


class ReportOut(BaseModel):
    session_id: str
    total_score: int
    product_thinking: int
    data_ability: int
    project_depth: int
    expression_logic: int
    business_understanding: int
    per_question: list
    improvement_suggestions: list
    reference_answers: list
    target_company: str | None = None
    target_position: str | None = None
    interview_round: str | None = None


@router.get("/{session_id}/report", response_model=ReportOut)
async def get_report(session_id: str, db: Session = Depends(get_db)):
    """Get evaluation report for a session."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.score_json:
        raise HTTPException(status_code=400, detail="Report not ready yet")

    profile = db.query(JobProfile).filter(JobProfile.profile_id == session.profile_id).first()
    score = session.score_json

    return ReportOut(
        session_id=session.session_id,
        total_score=score.get("total_score", 0),
        product_thinking=score.get("product_thinking", 0),
        data_ability=score.get("data_ability", 0),
        project_depth=score.get("project_depth", 0),
        expression_logic=score.get("expression_logic", 0),
        business_understanding=score.get("business_understanding", 0),
        per_question=score.get("per_question", []),
        improvement_suggestions=score.get("improvement_suggestions", []),
        reference_answers=score.get("reference_answers", []),
        target_company=profile.target_company if profile else None,
        target_position=profile.target_position if profile else None,
        interview_round=session.interview_round.value if session.interview_round else None,
    )
