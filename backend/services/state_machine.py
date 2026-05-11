"""
Interview state machine logic.
TODO: M3 - Implement state transitions and follow-up counter.
"""

from enum import Enum


class InterviewState(str, Enum):
    idle = "idle"
    self_intro = "self_intro"
    topic_question = "topic_question"
    follow_up = "follow_up"
    wrap_up = "wrap_up"
    evaluation = "evaluation"


MAX_FOLLOW_UP = 3


def should_force_transition(follow_up_count: int) -> bool:
    """Check if follow-up count has reached the hard limit."""
    return follow_up_count >= MAX_FOLLOW_UP


def get_state_description(state: InterviewState) -> str:
    descriptions = {
        InterviewState.idle: "等待用户开始",
        InterviewState.self_intro: "候选人自我介绍",
        InterviewState.topic_question: "主题提问",
        InterviewState.follow_up: "追问深挖",
        InterviewState.wrap_up: "收尾反问",
        InterviewState.evaluation: "评估评分",
    }
    return descriptions.get(state, "未知状态")
