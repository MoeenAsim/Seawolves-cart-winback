from app.models.cart import Cart
from app.models.eligibility import EligibilityResult
from app.models.recommendation import (
    Decision,
    OfferLLMOutput,
    OfferRecommendation,
    OfferType,
)
from app.services.llm_service import LLMService


SYSTEM_PROMPT = """
You are the Offer Strategy Agent for a sports ticket
cart win-back system.

Your responsibility is to choose the most appropriate
win-back intervention for an already-eligible cart.

The Eligibility Agent has already decided that the cart
is worth considering.

Your goal is to choose the LEAST COSTLY intervention that
has a reasonable chance of recovering the ticket purchase.

AVAILABLE INTERVENTIONS:

1. REMINDER
   Use when the customer already shows strong purchase
   intent and a discount is unnecessary.

2. FIRST_PURCHASE
   Use for a new customer with no previous purchases when
   a small incentive could reduce friction.

3. DISCOUNT
   Use when a modest discount is justified by the available
   evidence.

4. NONE
   Use when the available evidence does not support an
   intervention.

BUSINESS PRINCIPLES:

- Do not automatically discount high-value carts.
- Loyal customers with recent abandonment often only need
  a reminder.
- New customers can be good opportunities even without
  previous purchase history.
- Prefer the smallest useful incentive.
- Avoid unnecessary margin erosion.
- Never invent customer preferences or facts.
- Use only the supplied cart data and eligibility signals.
- Never recommend more than 15% discount.
- A discount should normally be no more than 10% unless
  there is a compelling reason.
- First-purchase incentives should normally be exactly 5%.
- If a reminder is sufficient, do not recommend a discount.
- The final recommendation will be checked by deterministic
  business policies.

IMPORTANT:

You are choosing the intervention strategy only.

The application will generate the final customer-facing
message deterministically.

Therefore, do NOT rely on your customer_message field
being used as the final message.

CUSTOMER MESSAGE RULES:

Any proposed message must:

- be concise and professional
- refer specifically to Seawolves tickets or the ticket purchase
- not mention AI
- not mention internal scoring
- not mention eligibility decisions
- not mention internal business rules
- not invent customer preferences
- not invent customer behavior
- not invent deadlines
- not create artificial urgency
- not promise ticket availability
- not claim tickets are reserved or held
- not claim the customer viewed something unless provided
- not mention an account unless account information is provided
- not mention links
- not mention following a link
- not mention visiting a website
- not mention clicking anything
- not use generic e-commerce wording such as "items in your cart"

Return only the requested structured result.
"""


class OfferStrategyAgent:

    def __init__(self):
        self.llm = LLMService()

    def recommend(
        self,
        cart: Cart,
        eligibility: EligibilityResult,
    ) -> OfferRecommendation:

        # =========================================================
        # STEP 1
        # If eligibility says NO_ACTION, do not ask the LLM
        # to invent an offer.
        # =========================================================

        if eligibility.decision == "no_action":
            return OfferRecommendation(
                cart_id=cart.cart_id,
                decision=Decision.NO_ACTION,
                priority=eligibility.priority,
                offer_type=OfferType.NONE,
                discount_percent=None,
                offer_description=(
                    "No win-back action recommended."
                ),
                reason=(
                    "Eligibility agent did not recommend "
                    "intervention."
                ),
                customer_message="",
            )

        # =========================================================
        # STEP 2
        # Prepare trusted context for the Offer Strategy Agent.
        # =========================================================

        user_prompt = f"""
Choose the most appropriate win-back intervention for
this eligible Seawolves ticket cart.

CART INFORMATION

Cart ID:
{cart.cart_id}

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


TRUSTED ELIGIBILITY SIGNALS

{", ".join(eligibility.signals)}


ELIGIBILITY DECISION

{eligibility.decision.value}


ELIGIBILITY PRIORITY

{eligibility.priority.value}


ELIGIBILITY REASONING

{eligibility.reason}


TASK

Choose exactly one intervention:

- reminder
- first_purchase
- discount
- none

DECISION GUIDANCE:

Use reminder when:
- the customer has strong purchase history
- abandonment is recent
- a discount is unnecessary

Use first_purchase when:
- lifetime_tickets is 0
- the cart is recent and meaningful
- email opt-in is true

Use discount only when:
- a modest discount is genuinely justified
- the evidence supports an incentive
- the discount is no more than 10% normally
- the discount never exceeds 15%

For first_purchase, use exactly 5%.

Avoid unnecessary discounting.

Do not invent information.

The final customer message will be generated
deterministically by the application.
"""


        # =========================================================
        # STEP 3
        # Ask Gemini for structured strategy output.
        #
        # If Gemini fails, use a conservative fallback.
        # =========================================================

        try:

            llm_result = self.llm.generate_structured(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                response_model=OfferLLMOutput,
            )

        except Exception:

            return self._safe_fallback(
                cart=cart,
                eligibility=eligibility,
            )

        # =========================================================
        # STEP 4
        # Normalize the LLM result.
        #
        # Deterministic code has final authority over:
        # - discount limits
        # - first-purchase discount
        # - customer message
        # =========================================================

        offer_type = llm_result.offer_type

        discount_percent = (
            llm_result.discount_percent
        )

        # ---------------------------------------------------------
        # First-purchase offers must use the standard 5%.
        # ---------------------------------------------------------

        if offer_type == OfferType.FIRST_PURCHASE:

            discount_percent = 5.0

        # ---------------------------------------------------------
        # Reminder must NEVER contain a discount.
        # ---------------------------------------------------------

        elif offer_type == OfferType.REMINDER:

            discount_percent = None

        # ---------------------------------------------------------
        # NONE must NEVER contain a discount.
        # ---------------------------------------------------------

        elif offer_type == OfferType.NONE:

            discount_percent = None

        # ---------------------------------------------------------
        # Generic discount:
        #
        # Keep it within the approved deterministic maximum.
        # The policy engine will perform the final validation.
        # ---------------------------------------------------------

        elif offer_type == OfferType.DISCOUNT:

            if discount_percent is None:
                discount_percent = 10.0

            discount_percent = max(
                0.0,
                min(
                    float(discount_percent),
                    15.0,
                ),
            )

        # =========================================================
        # STEP 5
        # Build deterministic offer description.
        # =========================================================

        offer_description = (
            self._build_offer_description(
                offer_type=offer_type,
                discount_percent=discount_percent,
            )
        )

        # =========================================================
        # STEP 6
        # Build deterministic customer-facing message.
        #
        # IMPORTANT:
        # We intentionally DO NOT use:
        #
        #     llm_result.customer_message
        #
        # This prevents unsafe/random phrases generated by the LLM.
        # =========================================================

        customer_message = (
            self._build_customer_message(
                offer_type=offer_type,
                discount_percent=discount_percent,
            )
        )

        # =========================================================
        # STEP 7
        # Build trusted application-level recommendation.
        # =========================================================

        return OfferRecommendation(
            cart_id=cart.cart_id,
            decision=Decision.ACT,
            priority=eligibility.priority,
            offer_type=offer_type,
            discount_percent=discount_percent,
            offer_description=offer_description,
            reason=llm_result.reason,
            customer_message=customer_message,
        )

    # =============================================================
    # SAFE FALLBACK
    # =============================================================

    @staticmethod
    def _safe_fallback(
        cart: Cart,
        eligibility: EligibilityResult,
    ) -> OfferRecommendation:
        """
        Conservative deterministic fallback.

        If the Offer Strategy Agent is unavailable,
        choose the lowest-cost intervention:
        a reminder without a discount.
        """

        return OfferRecommendation(
            cart_id=cart.cart_id,
            decision=Decision.ACT,
            priority=eligibility.priority,
            offer_type=OfferType.REMINDER,
            discount_percent=None,
            offer_description=(
                "Reminder to complete the Seawolves "
                "ticket purchase."
            ),
            reason=(
                "The offer strategy model was unavailable. "
                "A conservative reminder was selected as "
                "the lowest-cost fallback and should be "
                "reviewed by a marketer before sending."
            ),
            customer_message=(
                "Your Seawolves ticket purchase is still "
                "in progress. You can review your selection "
                "and complete your purchase when you are ready."
            ),
            risk_flags=[
                "llm_fallback",
            ],
        )

    # =============================================================
    # OFFER DESCRIPTION
    # =============================================================

    @staticmethod
    def _build_offer_description(
        offer_type: OfferType,
        discount_percent: float | None,
    ) -> str:

        if offer_type == OfferType.REMINDER:

            return (
                "Reminder to complete the Seawolves "
                "ticket purchase."
            )

        if offer_type == OfferType.FIRST_PURCHASE:

            discount = (
                discount_percent
                if discount_percent is not None
                else 5.0
            )

            return (
                f"{discount:g}% first-purchase discount."
            )

        if offer_type == OfferType.DISCOUNT:

            discount = (
                discount_percent
                if discount_percent is not None
                else 10.0
            )

            return (
                f"{discount:g}% win-back discount."
            )

        return (
            "No win-back action recommended."
        )

    # =============================================================
    # DETERMINISTIC CUSTOMER MESSAGE
    # =============================================================

    @staticmethod
    def _build_customer_message(
        offer_type: OfferType,
        discount_percent: float | None,
    ) -> str:
        """
        Generate safe customer-facing copy.

        The LLM does NOT control this message.

        This prevents unsupported phrases such as:
        - visit the site
        - follow the link
        - click here
        - today
        - tickets are reserved
        - tickets are available
        - seats are being held
        """

        # ---------------------------------------------------------
        # REMINDER
        # ---------------------------------------------------------

        if offer_type == OfferType.REMINDER:

            return (
                "Your Seawolves ticket purchase is still "
                "in progress. You can review your selection "
                "and complete your purchase when you are ready."
            )

        # ---------------------------------------------------------
        # FIRST PURCHASE
        # ---------------------------------------------------------

        if offer_type == OfferType.FIRST_PURCHASE:

            discount = (
                discount_percent
                if discount_percent is not None
                else 5.0
            )

            return (
                "Complete your first Seawolves ticket "
                f"purchase and receive {discount:g}% off."
            )

        # ---------------------------------------------------------
        # GENERIC DISCOUNT
        # ---------------------------------------------------------

        if offer_type == OfferType.DISCOUNT:

            discount = (
                discount_percent
                if discount_percent is not None
                else 10.0
            )

            return (
                "Complete your Seawolves ticket purchase "
                f"and receive {discount:g}% off."
            )

        # ---------------------------------------------------------
        # NONE
        # ---------------------------------------------------------

        return ""