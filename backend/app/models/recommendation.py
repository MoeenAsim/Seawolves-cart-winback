from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ACT = "act"
    NO_ACTION = "no_action"


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OfferType(str, Enum):
    NONE = "none"
    REMINDER = "reminder"
    DISCOUNT = "discount"
    FIRST_PURCHASE = "first_purchase"


class OfferLLMOutput(BaseModel):
    """
    Structured output produced by the Offer Strategy Agent.

    The LLM decides what intervention it recommends,
    but deterministic policy code will validate it afterward.
    """

    offer_type: OfferType

    discount_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    reason: str

    customer_message: str


class OfferRecommendation(BaseModel):
    """
    Final application-level recommendation.

    This combines:
    - eligibility decision
    - offer strategy
    - policy validation
    """

    cart_id: str
    decision: Decision
    priority: Priority

    offer_type: OfferType

    discount_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    offer_description: str

    reason: str

    customer_message: str

    risk_flags: list[str] = Field(
        default_factory=list
    )