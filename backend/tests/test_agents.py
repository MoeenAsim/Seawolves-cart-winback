from app.agents.eligibility_agent import EligibilityAgent
from app.models.cart import Cart
from app.models.eligibility import EligibilityDecision


def test_high_value_loyal_recent_cart():
    cart = Cart(
        cart_id="TEST-001",
        fan_id="TEST-FAN",
        seats=2,
        section="Lower Bowl",
        cart_value=96,
        abandoned_hours=3,
        lifetime_tickets=14,
        days_since_last_purchase=21,
        email_opt_in=True,
    )

    result = EligibilityAgent().evaluate(cart)

    assert result.decision == EligibilityDecision.ACT
    assert "strong_purchase_history" in result.signals


def test_no_email_opt_in():
    cart = Cart(
        cart_id="TEST-002",
        fan_id="TEST-FAN",
        seats=1,
        section="Lower Bowl",
        cart_value=58,
        abandoned_hours=3,
        lifetime_tickets=10,
        days_since_last_purchase=20,
        email_opt_in=False,
    )

    result = EligibilityAgent().evaluate(cart)

    assert result.decision == EligibilityDecision.NO_ACTION
    assert result.priority.value == "low"
    assert "email_not_opted_in" in result.signals