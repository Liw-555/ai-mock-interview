"""
Reflection & note-taking API for interview history.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import get_db, InterviewSession, SessionStatus

router = APIRouter()


class ReflectionNotes(BaseModel):
    notes: dict  # {question_idx: "user note text"}


class StarredQuestions(BaseModel):
    indices: list  # [0, 2, 5]


@router.get("/{session_id}/reflection")
async def get_reflection(session_id: str, db: Session = Depends(get_db)):
    """Get reflection summary and notes for a session."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session.session_id,
        "conversation_history": session.conversation_history or [],
        "reflection_summary": session.reflection_summary,
        "reflection_notes": session.reflection_notes or {},
        "starred_questions": session.starred_questions or [],
        "score_json": session.score_json,
    }


@router.post("/{session_id}/reflection/generate")
async def generate_reflection(session_id: str, db: Session = Depends(get_db)):
    """Generate AI reflection summary from conversation history."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    history = list(session.conversation_history or [])
    if not history:
        raise HTTPException(status_code=400, detail="No conversation history")

    summary = _build_reflection(history, session.score_json)
    session.reflection_summary = summary
    db.commit()
    return {"reflection_summary": summary}


@router.post("/{session_id}/reflection/notes")
async def save_reflection_notes(session_id: str, data: ReflectionNotes, db: Session = Depends(get_db)):
    """Save user's reflection notes."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.reflection_notes = data.notes
    db.commit()
    return {"message": "Notes saved"}


@router.post("/{session_id}/reflection/stars")
async def save_starred_questions(session_id: str, data: StarredQuestions, db: Session = Depends(get_db)):
    """Save starred question indices."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.starred_questions = data.indices
    db.commit()
    return {"message": "Stars saved"}


def _build_reflection(history: list, score_json: dict | None) -> str:
    """Build a reflection summary from conversation history (rule-based MVP)."""
    user_msgs = [m for m in history if m.get("role") == "user"]
    ai_msgs = [m for m in history if m.get("role") == "ai" and "能否再详细展开" not in m.get("content", "")]

    total_chars = sum(len(m.get("content", "")) for m in user_msgs)
    avg_len = total_chars / len(user_msgs) if user_msgs else 0

    lines = ["## 面试反思总结", ""]

    # Overall performance
    lines.append("### 整体表现")
    if avg_len > 100:
        lines.append("你的回答整体较为充实，能够围绕问题展开论述。继续保持！")
    elif avg_len > 50:
        lines.append("你的回答基本到位，但部分题目可以更加深入。建议多准备具体案例。")
    else:
        lines.append("你的回答整体偏简短。面试中建议用 STAR 法则组织内容，每个回答尽量覆盖背景、行动、结果。")
    lines.append("")

    # Per-question highlights
    lines.append("### 逐题亮点与不足")
    q_idx = 0
    for i, msg in enumerate(history):
        if msg.get("role") != "ai":
            continue
        content = msg.get("content", "")
        if "能否再详细展开" in content:
            continue
        q_idx += 1
        user_answer = ""
        if i + 1 < len(history) and history[i + 1].get("role") == "user":
            user_answer = history[i + 1].get("content", "")

        if len(user_answer) < 30:
            lines.append(f"**Q{q_idx}**：回答偏短，建议补充更多细节。")
        elif len(user_answer) > 150:
            lines.append(f"**Q{q_idx}**：回答较为充分，表达完整。")
        else:
            lines.append(f"**Q{q_idx}**：回答基本到位，可以在结构化方面再提升。")
    lines.append("")

    # Score-based suggestions
    lines.append("### 改进建议")
    if score_json:
        dims = {
            "product_thinking": "产品思维",
            "data_ability": "数据能力",
            "project_depth": "项目深度",
            "expression_logic": "表达逻辑",
            "business_understanding": "业务理解",
        }
        low_dims = []
        for k, label in dims.items():
            score = score_json.get(k, 0)
            if score <= 2:
                low_dims.append(f"{label}（{score}分）需要重点加强")
        if low_dims:
            lines.extend(low_dims)
        else:
            lines.append("各维度表现均衡，继续保持！建议针对薄弱维度做专项练习。")
    else:
        lines.append("暂无评分数据，完成面试后可查看详细改进建议。")

    return "\n".join(lines)
