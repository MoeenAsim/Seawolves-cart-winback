from app.agents.eligibility_agent import EligibilityAgent
from app.agents.offer_agent import OfferStrategyAgent
from app.models.cart import Cart
from app.models.eligibility import (
    EligibilityDecision,
    EligibilityResult,
    Priority,
)
from app.models.recommendation import (
    Decision,
    OfferType,
)


class FailingLLM:
    """
    Fake LLM used to simulate a Gemini/API failure.

    This allows us to test failure handling without
    actually taking the API offline.
    """

    def generate_structured(
        self,
        *args,
        **kwargs,
    ):
        raise RuntimeError(
            "Simulated LLM outage"
        )


def build_test_cart() -> Cart:
    return Cart(
        cart_id="FALLBACK-001",
        fan_id="TEST-FAN",
        seats=2,
        section="Lower Bowl",
        cart_value=96,
        abandoned_hours=3,
        lifetime_tickets=14,
        days_since_last_purchase=21,
        email_opt_in=True,
    )


def test_eligibility_llm_failure_fails_closed():
    """
    If the Eligibility Agent cannot reach the LLM,
    it must safely return NO_ACTION rather than guessing.
    """

    agent = EligibilityAgent()

    # Replace the real Gemini service with our failing fake.
    agent.llm = FailingLLM()

    result = agent.evaluate(
        build_test_cart()
    )

    assert result.decision == EligibilityDecision.NO_ACTION
    assert result.priority == Priority.LOW

    assert (
        "unavailable"
        in result.reason.lower()
    )


def test_offer_llm_failure_uses_conservative_fallback():
    """
    If eligibility is already ACT but the Offer Agent
    cannot reach the LLM, the system should fall back
    to a zero-discount reminder.
    """

    agent = OfferStrategyAgent()

    # Replace Gemini with the simulated failing service.
    agent.llm = FailingLLM()

    eligibility = EligibilityResult(
        cart_id="FALLBACK-001",
        decision=EligibilityDecision.ACT,
        priority=Priority.HIGH,
        reason=(
            "Recent abandonment and strong purchase "
            "history support intervention."
        ),
        signals=[
            "recent_abandonment",
            "strong_purchase_history",
        ],
    )

    result = agent.recommend(
        cart=build_test_cart(),
        eligibility=eligibility,
    )

    assert result.decision == Decision.ACT

    assert result.offer_type == OfferType.REMINDER

    assert result.discount_percent is None

    assert "llm_fallback" in result.risk_flags