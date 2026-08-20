from app.models.cart import Cart
from app.models.recommendation import (
    Decision,
    OfferRecommendation,
    OfferType,
    Priority,
)
from app.policies.policy_engine import (
    is_safe_to_show_to_marketer,
    validate_recommendation,
)


def make_cart(email_opt_in=True):
    return Cart(
        cart_id="TEST-001",
        fan_id="TEST-FAN",
        seats=2,
        section="Lower Bowl",
        cart_value=100,
        abandoned_hours=3,
        lifetime_tickets=5,
        days_since_last_purchase=30,
        email_opt_in=email_opt_in,
    )


def test_discount_within_policy_is_safe():
    cart = make_cart()

    recommendation = OfferRecommendation(
        cart_id=cart.cart_id,
        decision=Decision.ACT,
        priority=Priority.MEDIUM,
        offer_type=OfferType.DISCOUNT,
        discount_percent=10,
        offer_description="10% discount",
        reason="Recent cart abandonment",
        customer_message="Complete your purchase and save 10%.",
    )

    validated = validate_recommendation(
        cart,
        recommendation,
    )

    assert "discount_exceeds_policy" not in validated.risk_flags
    assert is_safe_to_show_to_marketer(
        cart,
        validated,
    )


def test_discount_above_policy_is_blocked():
    cart = make_cart()

    recommendation = OfferRecommendation(
        cart_id=cart.cart_id,
        decision=Decision.ACT,
        priority=Priority.MEDIUM,
        offer_type=OfferType.DISCOUNT,
        discount_percent=25,
        offer_description="25% discount",
        reason="Recent cart abandonment",
        customer_message="Complete your purchase and save 25%.",
    )

    validated = validate_recommendation(
        cart,
        recommendation,
    )

    assert "discount_exceeds_policy" in validated.risk_flags

    assert not is_safe_to_show_to_marketer(
        cart,
        validated,
    )


def test_non_opted_in_fan_is_blocked():
    cart = make_cart(email_opt_in=False)

    recommendation = OfferRecommendation(
        cart_id=cart.cart_id,
        decision=Decision.ACT,
        priority=Priority.MEDIUM,
        offer_type=OfferType.DISCOUNT,
        discount_percent=10,
        offer_description="10% discount",
        reason="Recent cart abandonment",
        customer_message="Complete your purchase and save 10%.",
    )

    validated = validate_recommendation(
        cart,
        recommendation,
    )

    assert "email_not_opted_in" in validated.risk_flags

    assert not is_safe_to_show_to_marketer(
        cart,
        validated,
    )