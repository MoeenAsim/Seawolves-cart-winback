from enum import Enum

from pydantic import BaseModel


class EligibilityDecision(str, Enum):
    ACT = "act"
    NO_ACTION = "no_action"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EligibilityLLMOutput(BaseModel):
    decision: EligibilityDecision
    priority: Priority
    reason: str


class EligibilityResult(BaseModel):
    cart_id: str
    decision: EligibilityDecision
    priority: Priority
    reason: str
    signals: list[str]