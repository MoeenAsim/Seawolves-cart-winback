from app.models.cart import Cart
from app.models.recommendation import OfferRecommendation


MAX_DISCOUNT_PERCENT = 15


def validate_recommendation(
    cart: Cart,
    recommendation: OfferRecommendation,
) -> OfferRecommendation:
    """
    Apply deterministic business and safety policies
    to an agent-generated recommendation.
    """

    risk_flags = list(recommendation.risk_flags)

    # ---------------------------------------------------------
    # NO_ACTION recommendations do not need communication
    # policy validation because there is no action to send.
    # ---------------------------------------------------------
    if recommendation.decision.value == "no_action":
        recommendation.risk_flags = list(
            dict.fromkeys(risk_flags)
        )
        return recommendation

    # ---------------------------------------------------------
    # 1. Communication permission check
    #
    # Any actionable email-based recommendation requires
    # explicit email opt-in.
    # ---------------------------------------------------------
    if not cart.email_opt_in:
        risk_flags.append("email_not_opted_in")

    # ---------------------------------------------------------
    # 2. Maximum discount check
    #
    # The model must never recommend a discount greater than
    # the business-approved maximum.
    # ---------------------------------------------------------
    if (
        recommendation.discount_percent is not None
        and recommendation.discount_percent > MAX_DISCOUNT_PERCENT
    ):
        risk_flags.append("discount_exceeds_policy")

    # ---------------------------------------------------------
    # 3. Discount / offer type consistency check
    #
    # A discount is only valid for:
    # - discount
    # - first_purchase
    #
    # Example:
    # reminder + 10% discount = INVALID
    # ---------------------------------------------------------
    if (
        recommendation.discount_percent is not None
        and recommendation.offer_type.value
        not in {"discount", "first_purchase"}
    ):
        risk_flags.append(
            "invalid_discount_offer_type"
        )

    # ---------------------------------------------------------
    # 4. Message safety validation
    #
    # The message validator runs in the orchestrator.
    # If it finds an unsafe phrase, those flags are already
    # present here and will be preserved.
    #
    # This section also makes the policy engine responsible
    # for recognizing those flags as a blocking condition.
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Remove duplicate risk flags while preserving order.
    # ---------------------------------------------------------
    recommendation.risk_flags = list(
        dict.fromkeys(risk_flags)
    )

    return recommendation


def is_safe_to_show_to_marketer(
    cart: Cart,
    recommendation: OfferRecommendation,
) -> bool:
    """
    Final deterministic safety gate before a recommendation
    is shown as safe for marketer approval.
    """

    # ---------------------------------------------------------
    # NO_ACTION recommendations are inherently safe because
    # there is no customer-facing action to send.
    # ---------------------------------------------------------
    if recommendation.decision.value == "no_action":
        return True

    # ---------------------------------------------------------
    # Actionable email recommendations require explicit
    # email opt-in.
    # ---------------------------------------------------------
    if not cart.email_opt_in:
        return False

    # ---------------------------------------------------------
    # Never allow a discount above the business limit.
    # ---------------------------------------------------------
    if "discount_exceeds_policy" in recommendation.risk_flags:
        return False

    # ---------------------------------------------------------
    # Never allow an invalid discount / offer combination.
    # ---------------------------------------------------------
    if "invalid_discount_offer_type" in recommendation.risk_flags:
        return False

    # ---------------------------------------------------------
    # Never allow an AI-generated customer message containing
    # an unsupported operational or urgency claim.
    #
    # Examples:
    # - follow the link
    # - through your account
    # - tickets are available
    # - today
    # - act now
    # ---------------------------------------------------------
    if any(
        flag.startswith("unsafe_message_phrase:")
        for flag in recommendation.risk_flags
    ):
        return False

    return True