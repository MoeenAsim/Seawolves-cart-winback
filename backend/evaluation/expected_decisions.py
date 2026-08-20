from dataclasses import dataclass


@dataclass(frozen=True)
class ExpectedBehavior:
    cart_id: str
    expected_decision: str
    expected_offer_type: str | None
    expected_discount: float | None
    reason: str


EXPECTED_BEHAVIOR = [
    ExpectedBehavior(
        cart_id="C-1001",
        expected_decision="act",
        expected_offer_type="reminder",
        expected_discount=None,
        reason=(
            "Recent abandonment plus strong purchase history "
            "supports a low-cost reminder."
        ),
    ),
    ExpectedBehavior(
        cart_id="C-1002",
        expected_decision="act",
        expected_offer_type="first_purchase",
        expected_discount=5,
        reason=(
            "Recent meaningful cart from a new customer with "
            "email opt-in supports a modest first-purchase incentive."
        ),
    ),
    ExpectedBehavior(
        cart_id="C-1003",
        expected_decision="no_action",
        expected_offer_type="none",
        expected_discount=None,
        reason=(
            "Email opt-in is absent, so no email-based intervention "
            "should be proposed."
        ),
    ),
    ExpectedBehavior(
        cart_id="C-1004",
        expected_decision="act",
        expected_offer_type="reminder",
        expected_discount=None,
        reason=(
            "Very recent abandonment and strong loyalty support "
            "a reminder without discounting."
        ),
    ),
    ExpectedBehavior(
        cart_id="C-1005",
        expected_decision="no_action",
        expected_offer_type="none",
        expected_discount=None,
        reason=(
            "The cart is highly stale with weak recent engagement."
        ),
    ),
]