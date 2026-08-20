from app.models.cart import Cart


def extract_signals(cart: Cart) -> list[str]:
    signals = []

    if cart.abandoned_hours <= 24:
        signals.append("recent_abandonment")
    elif cart.abandoned_hours <= 48:
        signals.append("moderately_recent_abandonment")
    elif cart.abandoned_hours > 72:
        signals.append("stale_cart")

    if cart.lifetime_tickets >= 10:
        signals.append("strong_purchase_history")
    elif cart.lifetime_tickets >= 3:
        signals.append("some_purchase_history")
    elif cart.lifetime_tickets == 0:
        signals.append("new_customer")

    if cart.days_since_last_purchase is None:
        signals.append("never_purchased")
    elif cart.days_since_last_purchase <= 30:
        signals.append("recent_customer_activity")
    elif cart.days_since_last_purchase > 180:
        signals.append("long_purchase_gap")

    if cart.email_opt_in:
        signals.append("email_opted_in")
    else:
        signals.append("email_not_opted_in")

    if cart.cart_value >= 300:
        signals.append("high_value_cart")
    elif cart.cart_value >= 100:
        signals.append("medium_value_cart")
    else:
        signals.append("low_value_cart")

    return signals
