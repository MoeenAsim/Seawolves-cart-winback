from app.models.cart import Cart
from app.models.eligibility import (
    EligibilityDecision,
    EligibilityLLMOutput,
    EligibilityResult,
    Priority,
)
from app.services.llm_service import LLMService
from app.services.signal_service import extract_signals


# =========================================================
# BUSINESS THRESHOLDS
# =========================================================

# Carts older than this are considered too stale for
# automated win-back eligibility.
MAX_ACTIONABLE_ABANDONMENT_HOURS = 72

# A cart abandoned within this window is considered recent.
RECENT_CART_HOURS = 48

# A cart at or above this value represents a meaningful
# commercial opportunity.
MEANINGFUL_CART_VALUE = 100

# Strong customer engagement threshold.
STRONG_LIFETIME_TICKETS = 10

# Recent purchase threshold.
RECENT_PURCHASE_DAYS = 30


# =========================================================
# LLM SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are the Eligibility Agent for a sports ticket
cart win-back system.

Your ONLY responsibility is to decide whether a stale
ticket cart deserves marketer intervention.

You are NOT responsible for:

- choosing a discount
- choosing an offer type
- writing a customer message
- deciding whether a specific message should be sent

Your job is ONLY:

1. Determine whether intervention is justified.
2. Assign a priority.
3. Explain the decision using only supplied evidence.

Use only the facts and trusted signals provided in the input.

NEVER INVENT:

- previous purchases
- customer preferences
- communication permissions
- demographics
- customer intent
- account information
- ticket availability
- reservation status
- deadlines
- facts not present in the input

BUSINESS PRINCIPLES:

1. Recent abandonment is a positive signal.

2. Strong purchase history is a positive engagement signal.

3. Recent purchase activity indicates an engaged customer.

4. High cart value means the opportunity may be valuable,
   but high value alone does NOT justify intervention.

5. Customers without email opt-in must not receive an
   email-based win-back recommendation.

6. Very stale carts should generally receive NO_ACTION.

7. When evidence is weak or conflicting, prefer NO_ACTION.

8. Do not recommend aggressive intervention merely because
   cart value is high.

9. A new customer can still be a strong win-back candidate.

10. A cart abandoned within 48 hours with meaningful cart
    value and email opt-in may justify intervention even
    when the customer has no previous purchase history.

11. Lack of previous purchases should NOT automatically
    result in NO_ACTION for a recent, meaningful cart.

12. A first-purchase incentive may be appropriate for a new
    customer with a recent meaningful cart and email opt-in.

13. Prefer proportionate intervention. A high-intent customer
    may only need a reminder rather than a discount.

14. Do not treat the absence of purchase history as evidence
    that the customer is uninterested.

15. The goal is to identify commercially reasonable
    opportunities, not to maximize the number of carts acted on.

16. When two decisions are plausible, prefer the lower-risk
    intervention.

17. Do not use cart value alone to assign HIGH priority.
    Priority should reflect the combination of recency,
    engagement, and opportunity value.

DECISION GUIDANCE:

ACT:

Use when the available evidence provides a reasonable basis
for marketer intervention.

NO_ACTION:

Use when the cart is too stale, lacks meaningful evidence,
has conflicting signals, or intervention would be speculative.

PRIORITY:

HIGH:

Strong recent intent combined with meaningful customer
engagement or opportunity value.

MEDIUM:

Reasonable opportunity but weaker evidence or lower
engagement.

LOW:

Weak opportunity, stale cart, or marginal evidence.

IMPORTANT:

The Eligibility Agent must NOT select the actual offer.

Do NOT say:

- "Give 5% off"
- "Send a reminder"
- "Offer 10% discount"

Only decide whether the marketer should consider this cart
and assign its priority.

Return only the requested structured result.
"""


class EligibilityAgent:
    """
    Determines whether a stale cart deserves marketer
    intervention.

    Architecture:

        Cart
          |
          v
    Trusted Signal Extraction
          |
          v
    Hard Safety Rules
          |
          v
    Eligibility LLM
          |
          v
    Deterministic Reconciliation
          |
          v
    EligibilityResult

    The LLM provides judgment, but deterministic business
    rules remain the final authority for critical constraints.
    """

    def __init__(self):
        self.llm = LLMService()

    # =========================================================
    # PUBLIC ENTRY POINT
    # =========================================================

    def evaluate(
        self,
        cart: Cart,
    ) -> EligibilityResult:

        # -----------------------------------------------------
        # Step 1:
        # Extract trusted signals using deterministic
        # application logic.
        #
        # These signals are generated by our application,
        # not by the LLM.
        # -----------------------------------------------------

        signals = extract_signals(cart)

        # -----------------------------------------------------
        # Step 2:
        # HARD SAFETY RULE — EMAIL OPT-IN
        #
        # Communication permission must never be decided
        # by an LLM.
        # -----------------------------------------------------

        if not cart.email_opt_in:

            return EligibilityResult(
                cart_id=cart.cart_id,
                decision=EligibilityDecision.NO_ACTION,
                priority=Priority.LOW,
                reason=(
                    "No email action is permitted because "
                    "the fan has not opted into email "
                    "communication."
                ),
                signals=signals,
            )

        # -----------------------------------------------------
        # Step 3:
        # HARD BUSINESS RULE — VERY STALE CART
        #
        # A cart older than the maximum actionable window
        # should not be automatically revived by an LLM.
        #
        # This protects against the model recommending an
        # intervention for a commercially stale opportunity.
        # -----------------------------------------------------

        if (
            cart.abandoned_hours
            > MAX_ACTIONABLE_ABANDONMENT_HOURS
        ):

            return EligibilityResult(
                cart_id=cart.cart_id,
                decision=EligibilityDecision.NO_ACTION,
                priority=Priority.LOW,
                reason=(
                    "The cart is too stale for automated "
                    "win-back intervention."
                ),
                signals=signals,
            )

        # -----------------------------------------------------
        # Step 4:
        # Prepare trusted information for Gemini.
        #
        # Only information actually present in the cart
        # is provided.
        # -----------------------------------------------------

        user_prompt = f"""
Evaluate this stale Seawolves ticket cart.

CART INFORMATION

Cart ID:
{cart.cart_id}

Fan ID:
{cart.fan_id}

Seats:
{cart.seats}

Section:
{cart.section}

Cart value:
${cart.cart_value:.2f}

Hours since abandonment:
{cart.abandoned_hours}

Lifetime tickets:
{cart.lifetime_tickets}

Days since last purchase:
{cart.days_since_last_purchase}

Email opt-in:
{cart.email_opt_in}

TRUSTED SIGNALS

{", ".join(signals)}

TASK

Determine whether this cart deserves marketer intervention.

Return:

- decision: ACT or NO_ACTION
- priority: HIGH, MEDIUM, or LOW
- reason: concise explanation based only on supplied evidence

IMPORTANT:

Do NOT choose an offer.

Do NOT choose a discount.

Do NOT write a customer message.

Do NOT invent facts.

A new customer with zero previous purchases can still be
eligible when the cart is recent, meaningful, and email
opt-in is present.

A loyal customer with strong recent intent may also be
eligible even when no discount is necessary.

Recent abandonment should generally carry more weight than
absence of purchase history.

If the evidence is weak or conflicting, prefer NO_ACTION.
"""

        # -----------------------------------------------------
        # Step 5:
        # Ask Gemini for structured eligibility.
        #
        # The LLM is allowed to fail.
        # We fail CLOSED rather than guessing.
        # -----------------------------------------------------

        try:

            llm_result = self.llm.generate_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=EligibilityLLMOutput,
            )

        except Exception:

            # -------------------------------------------------
            # SAFE FALLBACK
            #
            # If the model is unavailable, malformed, times
            # out, rate-limited, etc., we do not create an
            # automated opportunity from incomplete reasoning.
            # -------------------------------------------------

            return EligibilityResult(
                cart_id=cart.cart_id,
                decision=EligibilityDecision.NO_ACTION,
                priority=Priority.LOW,
                reason=(
                    "Eligibility analysis was unavailable, "
                    "so the cart was safely held for manual "
                    "review."
                ),
                signals=signals,
            )

        # -----------------------------------------------------
        # Step 6:
        # Reconcile LLM output with deterministic business
        # rules.
        #
        # This is important because an LLM can produce a
        # plausible-looking but commercially inconsistent
        # decision.
        # -----------------------------------------------------

        return self._reconcile_with_business_rules(
            cart=cart,
            llm_result=llm_result,
            signals=signals,
        )

    # =========================================================
    # DETERMINISTIC RECONCILIATION
    # =========================================================

    @staticmethod
    def _reconcile_with_business_rules(
        cart: Cart,
        llm_result: EligibilityLLMOutput,
        signals: list[str],
    ) -> EligibilityResult:
        """
        Reconcile probabilistic LLM output with deterministic
        business constraints.

        The LLM can reason about the opportunity, but strong
        trusted business evidence prevents the system from
        silently discarding a clearly valuable recent cart.

        This layer also prevents the LLM from activating a
        very stale opportunity.
        """

        # -----------------------------------------------------
        # Derived deterministic signals
        # -----------------------------------------------------

        recent_cart = (
            cart.abandoned_hours
            <= RECENT_CART_HOURS
        )

        meaningful_value = (
            cart.cart_value
            >= MEANINGFUL_CART_VALUE
        )

        strong_history = (
            cart.lifetime_tickets
            >= STRONG_LIFETIME_TICKETS
        )

        recent_purchase = (
            cart.days_since_last_purchase
            is not None
            and cart.days_since_last_purchase
            <= RECENT_PURCHASE_DAYS
        )

        # -----------------------------------------------------
        # Strong commercial opportunity
        #
        # We deliberately require multiple pieces of evidence.
        #
        # High cart value alone is NOT enough.
        # -----------------------------------------------------

        strong_opportunity = (
            cart.email_opt_in
            and recent_cart
            and (
                (
                    meaningful_value
                    and strong_history
                )
                or
                (
                    meaningful_value
                    and recent_purchase
                )
                or
                (
                    strong_history
                    and recent_purchase
                )
            )
        )

        # -----------------------------------------------------
        # Case 1:
        # Strong opportunity but LLM says NO_ACTION.
        #
        # Deterministic guard overrides the LLM because the
        # model has contradicted strong trusted evidence.
        # -----------------------------------------------------

        if (
            strong_opportunity
            and llm_result.decision
            == EligibilityDecision.NO_ACTION
        ):

            return EligibilityResult(
                cart_id=cart.cart_id,
                decision=EligibilityDecision.ACT,
                priority=Priority.HIGH,
                reason=(
                    "The eligibility model recommended no action, "
                    "but a deterministic business guard identified "
                    "a strong recent opportunity based on cart "
                    "recency, customer engagement, and commercial "
                    "value."
                ),
                signals=signals,
            )

        # -----------------------------------------------------
        # Case 2:
        # The LLM recommends ACT but the cart is stale.
        #
        # This should normally already be blocked by the hard
        # stale-cart rule above, but keeping the rule here makes
        # the reconciliation layer defensive if it is reused.
        # -----------------------------------------------------

        if (
            cart.abandoned_hours
            > MAX_ACTIONABLE_ABANDONMENT_HOURS
            and llm_result.decision
            == EligibilityDecision.ACT
        ):

            return EligibilityResult(
                cart_id=cart.cart_id,
                decision=EligibilityDecision.NO_ACTION,
                priority=Priority.LOW,
                reason=(
                    "The cart exceeds the maximum actionable "
                    "abandonment window, so automated win-back "
                    "intervention is not recommended."
                ),
                signals=signals,
            )

        # -----------------------------------------------------
        # Case 3:
        # LLM decision is consistent with deterministic rules.
        #
        # Trust the structured result.
        # -----------------------------------------------------

        return EligibilityResult(
            cart_id=cart.cart_id,
            decision=llm_result.decision,
            priority=llm_result.priority,
            reason=llm_result.reason,
            signals=signals,
        )