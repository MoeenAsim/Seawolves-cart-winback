from app.models.recommendation import OfferRecommendation


UNSAFE_PHRASES = {
    # Unsupported navigation / operational claims
    "follow the link",
    "click the link",
    "use the link",
    "link provided",
    "through your account",
    "return to the site",
    "visit the site",
    "log in",
    "login",

    # Unsupported availability / reservation claims
    "reserved for you",
    "held for you",
    "guaranteed availability",
    "tickets are available",
    "tickets are still available",
    "your seats are available",
    "your seats are reserved",
    "your seats are being held",

    # Unsupported generic cart language
    "items in your cart",

    # Artificial urgency
    "today",
    "tonight",
    "right now",
    "act now",
    "limited time",
    "last chance",
    "expires today",
    "expires tonight",
}


def validate_customer_message(
    recommendation: OfferRecommendation,
) -> list[str]:
    """
    Deterministically validate an AI-generated customer message.

    The purpose is to catch plausible-looking messages that
    contain unsupported operational claims or artificial urgency.
    """

    # There is no customer-facing message for NO_ACTION.
    if recommendation.decision.value == "no_action":
        return []

    message = recommendation.customer_message.lower()

    risk_flags: list[str] = []

    for phrase in UNSAFE_PHRASES:
        if phrase in message:
            risk_flags.append(
                f"unsafe_message_phrase:{phrase}"
            )

    return list(dict.fromkeys(risk_flags))