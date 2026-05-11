"""
Interview session API.
"""

import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.database import (
    get_db, InterviewSession, InterviewRound, InterviewerRole,
    InterviewerStyle, SessionStatus, Resume, JobProfile, User
)
from services.scorer import calculate_total_score, get_dimension_weights, get_dimension_names, get_empty_score
from services.prompt_selector import detect_position_category, POSITION_DIMENSIONS

router = APIRouter()


class SessionCreate(BaseModel):
    resume_id: str
    profile_id: str
    interview_round: str  # first, second, hr
    interviewer_role: str  # business, manager, hr
    interviewer_style: str = "professional"  # professional, gentle, pressure


class SessionOut(BaseModel):
    session_id: str
    resume_id: str
    profile_id: str
    interview_round: str
    interviewer_role: str
    interviewer_style: str
    status: str
    target_company: str | None = None
    target_position: str | None = None
    total_score: int | None = None
    conversation_history: list | None = None
    elapsed_seconds: int = 0
    started_at: datetime
    ended_at: datetime | None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    next_state: str
    topic: str | None
    is_follow_up: bool
    follow_up_count: int
    state_reason: str | None


# ─── Position-specific question banks ───

POSITION_QUESTIONS = {
    "pm": {
        "business": [
            "你好，我是{company}的面试官，负责{position}岗位的面试。请先简单介绍一下你自己。",
            "你为什么选择应聘{company}的{position}？",
            "请描述一下你在产品方面的核心优势，以及这些优势如何匹配{position}的要求。",
            "如果让你负责{company}的一个产品功能迭代，你会如何制定优先级？",
            "请分享一个你主导的产品项目，从需求发现到上线的完整过程。",
            "在团队协作中，如何处理与研发的需求分歧？请举例说明。",
            "你对我们{company}的产品有什么了解？你认为有什么可以改进的地方？",
            "你未来3-5年的职业规划是什么？希望在产品方向达到什么样的目标？",
        ],
        "hr": [
            "你好，我是{company}的HR。请先简单介绍一下你自己。",
            "你为什么选择离开当前的公司/学校，想要加入{company}？",
            "你期望的薪资范围是多少？",
            "你对我们{company}的企业文化有什么了解？",
            "你还有什么问题想要问我的吗？",
        ],
    },
    "ops": {
        "business": [
            "你好，我是{company}的面试官，负责{position}岗位的面试。请先简单介绍一下你自己。",
            "你为什么选择运营方向？产品和运营的区别你怎么看？",
            "请用AARRR模型分析一个你熟悉的产品的运营策略。",
            "如果让你为{company}设计一个拉新活动方案，你会怎么规划？",
            "请分享一个你参与的运营项目，你是如何衡量活动效果的？",
            "分析一个你常用的APP的运营亮点和不足。",
            "面对用户流失，你会从哪些维度分析和制定挽回策略？",
            "你未来3-5年在运营方向的职业规划是什么？",
        ],
        "hr": [
            "你好，我是{company}的HR。请先简单介绍一下你自己。",
            "运营工作节奏快，经常需要加班，你怎么看？",
            "你在项目中遇到过最大的困难是什么？怎么处理的？",
            "你觉得一个好的运营人需要哪些特质？",
            "你还有什么问题想要问我的吗？",
        ],
    },
    "da": {
        "business": [
            "你好，我是{company}的面试官，负责{position}岗位的面试。请先简单介绍一下你自己。",
            "请写一个SQL：找出每个用户消费金额最高的两个品类。",
            "GMV下降10%，你会如何定位原因？请给出分析框架。",
            "AB测试中如何计算样本量？z检验和t检验的区别是什么？",
            "请分享一个你用数据驱动业务决策的案例，重点讲分析思路。",
            "逻辑回归的原理是什么？过拟合怎么处理？",
            "如何设计一个用户分层体系？请给出具体方法。",
            "你未来3-5年在数据分析方向的职业规划是什么？",
        ],
        "hr": [
            "你好，我是{company}的HR。请先简单介绍一下你自己。",
            "你为什么选择数据分析而不是纯算法开发？",
            "如果业务方不认可你的分析结论，你会怎么处理？",
            "你觉得数据分析师最重要的能力是什么？",
            "你还有什么问题想要问我的吗？",
        ],
    },
    "algo": {
        "business": [
            "你好，我是{company}的面试官，负责{position}岗位的面试。请先简单介绍一下你自己。",
            "请讲解Transformer的Self-Attention计算过程，为什么需要Scale？",
            "XGBoost和LightGBM的核心区别是什么？各自适用什么场景？",
            "请分享一个你做过的推荐系统或NLP项目，重点讲模型选型理由。",
            "LoRA微调的原理是什么？和全量微调相比有什么优劣？",
            "RAG架构的工作原理是什么？如何解决幻觉问题？",
            "CTR提升34%，你怎么归因？如何排除其他因素影响？",
            "你未来3-5年在算法方向的职业规划是什么？",
        ],
        "hr": [
            "你好，我是{company}的HR。请先简单介绍一下你自己。",
            "你为什么选择工业界而不是继续做学术研究？",
            "模型上线后效果不及预期，你会怎么处理？",
            "你在项目中遇到过最大的技术瓶颈是什么？怎么解决的？",
            "你还有什么问题想要问我的吗？",
        ],
    },
    "dev": {
        "business": [
            "你好，我是{company}的面试官，负责{position}岗位的面试。请先简单介绍一下你自己。",
            "MySQL四种事务隔离级别分别解决什么问题？",
            "Redis的ZSET底层是怎么实现的？为什么用跳表？",
            "请分享一个你做过的系统设计或高并发项目，重点讲架构决策。",
            "手撕快排：请写出完整代码，分析时间复杂度。",
            "Kafka的Rebalance过程是怎样的？如何避免数据丢失？",
            "设计一个短链服务，如何保证高可用和高并发？",
            "你未来3-5年在研发方向的职业规划是什么？",
        ],
        "hr": [
            "你好，我是{company}的HR。请先简单介绍一下你自己。",
            "你为什么选择研发而不是产品或测试？",
            "和产品经理技术方案有分歧时，你怎么处理？",
            "线上出了紧急bug，你会怎么处理？",
            "你还有什么问题想要问我的吗？",
        ],
    },
}


@router.post("", response_model=SessionOut)
async def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    """Create a new interview session."""
    # Validate IDs
    resume = db.query(Resume).filter(Resume.resume_id == data.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    profile = db.query(JobProfile).filter(JobProfile.profile_id == data.profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Job profile not found")

    # Map enums
    round_map = {"first": InterviewRound.first, "second": InterviewRound.second, "hr": InterviewRound.hr}
    role_map = {"business": InterviewerRole.business, "manager": InterviewerRole.manager, "hr": InterviewerRole.hr}
    style_map = {"professional": InterviewerStyle.professional, "gentle": InterviewerStyle.gentle, "pressure": InterviewerStyle.pressure}

    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        user_id=resume.user_id,
        profile_id=data.profile_id,
        resume_id=data.resume_id,
        interview_round=round_map.get(data.interview_round, InterviewRound.first),
        interviewer_role=role_map.get(data.interviewer_role, InterviewerRole.business),
        interviewer_style=style_map.get(data.interviewer_style, InterviewerStyle.professional),
        conversation_history=[],
        status=SessionStatus.in_progress,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def _session_to_dict(session: InterviewSession, db: Session) -> dict:
    """Convert session ORM object to enriched dict with profile info."""
    profile = db.query(JobProfile).filter(JobProfile.profile_id == session.profile_id).first()
    return {
        "session_id": session.session_id,
        "resume_id": session.resume_id,
        "profile_id": session.profile_id,
        "interview_round": session.interview_round.value if session.interview_round else None,
        "interviewer_role": session.interviewer_role.value if session.interviewer_role else None,
        "interviewer_style": session.interviewer_style.value if session.interviewer_style else None,
        "status": session.status.value if session.status else None,
        "target_company": profile.target_company if profile else None,
        "target_position": profile.target_position if profile else None,
        "total_score": session.score_json.get("total_score") if session.score_json else None,
        "conversation_history": session.conversation_history,
        "elapsed_seconds": session.elapsed_seconds or 0,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
    }


@router.get("", response_model=List[SessionOut])
async def list_sessions(status: str | None = None, db: Session = Depends(get_db)):
    """List interview sessions, optionally filtered by status."""
    query = db.query(InterviewSession)
    if status:
        query = query.filter(InterviewSession.status == status)
    sessions = query.order_by(InterviewSession.started_at.desc()).all()
    return [_session_to_dict(s, db) for s in sessions]


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get session details."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _session_to_dict(session, db)


def _get_category_and_questions(session: InterviewSession, profile: JobProfile):
    """Detect position category and get the corresponding question bank."""
    category = detect_position_category(
        target_position=profile.target_position if profile else "",
        position_direction=profile.position_direction if profile else None,
    )
    is_hr = session.interview_round == InterviewRound.hr
    q_type = "hr" if is_hr else "business"
    questions = POSITION_QUESTIONS.get(category, POSITION_QUESTIONS["pm"]).get(q_type, POSITION_QUESTIONS["pm"]["business"])
    max_questions = 5 if is_hr else 8
    return category, questions, max_questions


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, req: ChatRequest, db: Session = Depends(get_db)):
    """Send a message to the AI interviewer and get response."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == SessionStatus.completed:
        raise HTTPException(status_code=400, detail="Session already completed")

    # Load related data
    profile = db.query(JobProfile).filter(JobProfile.profile_id == session.profile_id).first()
    resume = db.query(Resume).filter(Resume.resume_id == session.resume_id).first()
    company = profile.target_company if profile else "贵公司"
    position = profile.target_position if profile else "该岗位"

    # Detect position category and select question bank
    category, questions, max_questions = _get_category_and_questions(session, profile)

    # Initialize state tracking in conversation_history metadata
    history = list(session.conversation_history or [])
    is_init = req.message == "（面试开始）"

    # Append user's message first (skip for init marker)
    if not is_init:
        history.append({"role": "user", "content": req.message, "time": _now()})

    # Recalculate counts after appending user message
    ai_msg_count = sum(1 for m in history if m.get("role") == "ai")
    user_msg_count = sum(1 for m in history if m.get("role") == "user")

    # Compute follow-up count: skip user messages, count trailing follow-up AI messages
    follow_up_count = 0
    for i in range(len(history) - 1, -1, -1):
        msg = history[i]
        if msg.get("role") == "ai":
            if "能否再详细展开一下" in msg.get("content", ""):
                follow_up_count += 1
            else:
                break
        elif msg.get("role") == "user":
            continue  # Skip user messages to count consecutive follow-ups

    # Count formal questions (excluding follow-up prompts)
    formal_q_count = ai_msg_count - follow_up_count
    is_follow_up = False

    # Question bank with variable substitution
    def make_question(template: str) -> str:
        return template.replace("{company}", company).replace("{position}", position)

    # Determine next action
    if formal_q_count >= max_questions:
        # Interview is complete
        message = "好的，今天的面试就到这里。感谢你的参与，我们会尽快通知你结果。"
        session.status = SessionStatus.completed
        session.ended_at = datetime.now(timezone.utc)
    elif formal_q_count == 0:
        # First question (self-intro)
        message = make_question(questions[0])
    else:
        # Check if we should do follow-up (skip for self-intro answer)
        last_user_msg = req.message
        should_follow_up = (
            formal_q_count > 1
            and len(last_user_msg) < 20
            and follow_up_count < 3
            and user_msg_count >= ai_msg_count
        )
        if should_follow_up:
            message = "你的回答比较简短，能否再详细展开一下？"
            is_follow_up = True
        else:
            # Move to next question
            next_q_idx = min(formal_q_count, max_questions - 1)
            message = make_question(questions[next_q_idx])

    # Append AI response to history
    history.append({"role": "ai", "content": message, "time": _now()})
    session.conversation_history = history
    db.commit()
    db.refresh(session)

    return ChatResponse(
        message=message,
        next_state="topic_question" if ai_msg_count < max_questions else "completed",
        topic=None,
        is_follow_up=is_follow_up,
        follow_up_count=follow_up_count,
        state_reason=f"Rule-based question engine (category: {category})",
    )


def _now() -> str:
    from datetime import datetime
    d = datetime.now()
    return f"{d.hour}:{d.minute:02d}"


class PauseRequest(BaseModel):
    elapsed_seconds: int = 0


@router.post("/{session_id}/pause")
async def pause_session(session_id: str, body: PauseRequest = None, db: Session = Depends(get_db)):
    """Pause the session and save conversation history + elapsed time."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.paused
    if body and body.elapsed_seconds:
        session.elapsed_seconds = body.elapsed_seconds
    # TODO: Generate summary_at_pause (M6)
    db.commit()
    return {"message": "Session paused", "session_id": session_id, "elapsed_seconds": session.elapsed_seconds}


@router.post("/{session_id}/resume")
async def resume_session(session_id: str, db: Session = Depends(get_db)):
    """Resume a paused session."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.in_progress
    db.commit()
    return {"message": "Session resumed", "session_id": session_id}


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete an interview session."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}


@router.post("/{session_id}/end")
async def end_session(session_id: str, db: Session = Depends(get_db)):
    """End the session and trigger evaluation."""
    session = db.query(InterviewSession).filter(InterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.completed
    session.ended_at = datetime.now(timezone.utc)

    # Detect position category for position-specific scoring
    profile = db.query(JobProfile).filter(JobProfile.profile_id == session.profile_id).first()
    category = detect_position_category(
        target_position=profile.target_position if profile else "",
        position_direction=profile.position_direction if profile else None,
    )

    try:
        session.score_json = _generate_score_json(session, category)
    except Exception as e:
        import logging
        logging.exception("Failed to generate score_json for session %s", session_id)
        session.score_json = get_empty_score(category)
    db.commit()
    return {"message": "Session ended", "session_id": session_id}


def _generate_score_json(session: InterviewSession, category: str = "pm") -> dict:
    """Generate a rule-based score JSON from conversation history using position-specific dimensions."""
    from services.prompt_selector import get_position_suggestions

    history = list(session.conversation_history or [])
    user_msgs = [m for m in history if m.get("role") == "user"]
    ai_msgs = [m for m in history if m.get("role") == "ai"]

    if not user_msgs:
        return get_empty_score(category)

    total_chars = sum(len(m.get("content", "")) for m in user_msgs)
    avg_len = total_chars / len(user_msgs)

    # Count follow-up prompts (indicates insufficient detail)
    follow_up_count = sum(
        1 for m in ai_msgs if "能否再详细展开" in m.get("content", "")
    )
    penalty = min(1.5, follow_up_count * 0.5)

    # Get position-specific dimensions and compute scores
    dims = POSITION_DIMENSIONS.get(category, POSITION_DIMENSIONS["pm"])
    base = {}
    for i, (dim_key, dim_info) in enumerate(dims.items()):
        # Vary the divisor slightly per dimension to create score differentiation
        divisor = 45 + i * 3
        base[dim_key] = min(5, max(1, 1 + avg_len / divisor))

    dimensions = {k: max(1, round(v - penalty)) for k, v in base.items()}
    total = calculate_total_score(dimensions, category)

    # Build per-question reviews
    dim_names = get_dimension_names(category)
    per_question = []
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

        # Adjust per-question scores slightly based on answer length
        q_scores = dimensions.copy()
        if len(user_answer) < 30:
            q_scores = {k: max(1, v - 1) for k, v in q_scores.items()}
        elif len(user_answer) > 150:
            q_scores = {k: min(5, v + 1) for k, v in q_scores.items()}

        per_question.append({
            "question_summary": content[:60] + ("..." if len(content) > 60 else ""),
            "user_quote": user_answer[:300],
            "scores": q_scores,
            "comment": _generate_q_comment(q_scores, len(user_answer)),
        })

    # Build improvement suggestions using position-specific texts
    suggestion_texts = get_position_suggestions(category)

    suggestions = []
    for dim, score in dimensions.items():
        if score <= 2:
            priority = "高"
        elif score <= 3:
            priority = "中"
        else:
            continue
        suggestions.append({
            "dimension": dim_names.get(dim, dim),
            "score": score,
            "priority": priority,
            "suggestion": suggestion_texts.get(dim, "针对该维度加强练习，积累更多面试经验。"),
        })
    if not suggestions:
        suggestions.append({
            "dimension": "综合",
            "score": round(sum(dimensions.values()) / len(dimensions)),
            "priority": "低",
            "suggestion": "整体表现不错，继续保持！建议针对薄弱维度做专项练习。",
        })

    return {
        "total_score": total,
        **dimensions,
        "per_question": per_question,
        "improvement_suggestions": suggestions,
        "reference_answers": [],
    }


def _generate_q_comment(scores: dict, answer_len: int) -> str:
    if answer_len < 30:
        return "回答较为简短，建议补充更多细节和具体案例。"
    avg = sum(scores.values()) / len(scores)
    if avg >= 4:
        return "回答思路清晰，表达完整，展现了较好的专业素养。"
    elif avg >= 3:
        return "回答基本到位，可以在深度和结构化方面继续提升。"
    return "建议多结合过往项目经验，用STAR法则组织回答内容。"
