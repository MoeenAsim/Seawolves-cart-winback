from app.agents.eligibility_agent import EligibilityAgent
from app.agents.offer_agent import OfferStrategyAgent
from app.models.cart import Cart
from app.models.recommendation import OfferRecommendation
from app.policies.message_policy import validate_customer_message
from app.policies.policy_engine import (
    is_safe_to_show_to_marketer,
    validate_recommendation,
)


class WinBackOrchestrator:
    """
    Coordinates the complete cart win-back workflow.

    Flow:

        Cart
          ↓
        Signal Extraction
          ↓
        Eligibility Agent
          ↓
        Offer Strategy Agent
          ↓
        Business Policy Engine
          ↓
        Customer Message Validator
          ↓
        Safety Gate
          ↓
        Marketer
    """

    def __init__(self):
        self.eligibility_agent = EligibilityAgent()
        self.offer_agent = OfferStrategyAgent()

    def process_cart(self, cart: Cart) -> OfferRecommendation:

        # ---------------------------------------------------------
        # Step 1:
        # Determine whether the stale cart deserves intervention.
        # ---------------------------------------------------------
        eligibility = self.eligibility_agent.evaluate(cart)

        # ---------------------------------------------------------
        # Step 2:
        # If eligible, ask the Offer Strategy Agent to choose
        # the least costly appropriate intervention.
        #
        # If eligibility is NO_ACTION, the Offer Agent returns
        # a NO_ACTION recommendation without calling the LLM.
        # ---------------------------------------------------------
        recommendation = self.offer_agent.recommend(
            cart=cart,
            eligibility=eligibility,
        )

        # ---------------------------------------------------------
        # Step 3:
        # Apply deterministic business policies.
        #
        # Examples:
        # - maximum discount
        # - email permission
        # - valid offer/discount combinations
        # ---------------------------------------------------------
        recommendation = validate_recommendation(
            cart=cart,
            recommendation=recommendation,
        )

        # ---------------------------------------------------------
        # Step 4:
        # Validate the AI-generated customer-facing message.
        #
        # This catches plausible but unsupported claims such as:
        # - "follow the link"
        # - "tickets are available"
        # - "through your account"
        # - "today"
        # ---------------------------------------------------------
        message_flags = validate_customer_message(
            recommendation
        )

        recommendation.risk_flags.extend(
            message_flags
        )

        # Remove duplicate risk flags while preserving order.
        recommendation.risk_flags = list(
            dict.fromkeys(
                recommendation.risk_flags
            )
        )

        # ---------------------------------------------------------
        # Step 5:
        # Final deterministic safety gate.
        #
        # A recommendation is only considered safe when it passes
        # all business and communication policies.
        # ---------------------------------------------------------
        is_safe = is_safe_to_show_to_marketer(
            cart=cart,
            recommendation=recommendation,
        )

        # ---------------------------------------------------------
        # Step 6:
        # If any policy or message validation failed, explicitly
        # mark the recommendation as blocked.
        #
        # We keep the original recommendation visible so the
        # marketer can understand what the agent proposed and
        # edit or reject it.
        # ---------------------------------------------------------
        if (
            not is_safe
            and "blocked_by_policy"
            not in recommendation.risk_flags
        ):
            recommendation.risk_flags.append(
                "blocked_by_policy"
            )

        return recommendation

    def process_carts(
        self,
        carts: list[Cart],
    ) -> list[OfferRecommendation]:
        """
        Process a batch of stale carts independently.

        Each cart goes through the complete agentic workflow.
        """

        return [
            self.process_cart(cart)
            for cart in carts
        ]