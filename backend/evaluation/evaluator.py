from dataclasses import dataclass

from app.models.recommendation import OfferRecommendation

from evaluation.expected_decisions import EXPECTED_BEHAVIOR


@dataclass
class EvaluationReport:
    total_cases: int
    correct_decisions: int
    correct_offers: int
    correct_discounts: int
    policy_violations: int
    unsafe_messages: int

    @property
    def decision_accuracy(self) -> float:
        if self.total_cases == 0:
            return 0.0

        return (
            self.correct_decisions
            / self.total_cases
        )

    @property
    def offer_accuracy(self) -> float:
        actionable_cases = sum(
            1
            for expected in EXPECTED_BEHAVIOR
            if expected.expected_decision == "act"
        )

        if actionable_cases == 0:
            return 0.0

        return (
            self.correct_offers
            / actionable_cases
        )

    @property
    def discount_accuracy(self) -> float:
        actionable_cases = sum(
            1
            for expected in EXPECTED_BEHAVIOR
            if expected.expected_decision == "act"
        )

        if actionable_cases == 0:
            return 0.0

        return (
            self.correct_discounts
            / actionable_cases
        )


def evaluate_recommendations(
    recommendations: list[OfferRecommendation],
) -> EvaluationReport:

    recommendations_by_cart = {
        recommendation.cart_id: recommendation
        for recommendation in recommendations
    }

    correct_decisions = 0
    correct_offers = 0
    correct_discounts = 0
    policy_violations = 0
    unsafe_messages = 0

    for expected in EXPECTED_BEHAVIOR:

        actual = recommendations_by_cart.get(
            expected.cart_id
        )

        if actual is None:
            continue

        # ---------------------------------------------------------
        # Decision accuracy
        # ---------------------------------------------------------
        if actual.decision.value == expected.expected_decision:
            correct_decisions += 1

        # ---------------------------------------------------------
        # Offer type accuracy
        #
        # Only compare offer type for ACT cases.
        # ---------------------------------------------------------
        if expected.expected_decision == "act":
            if (
                actual.offer_type.value
                == expected.expected_offer_type
            ):
                correct_offers += 1

        # ---------------------------------------------------------
        # Discount accuracy
        # ---------------------------------------------------------
        if expected.expected_decision == "act":
            if (
                actual.discount_percent
                == expected.expected_discount
            ):
                correct_discounts += 1

        # ---------------------------------------------------------
        # Policy violations
        # ---------------------------------------------------------
        if any(
            flag in actual.risk_flags
            for flag in [
                "discount_exceeds_policy",
                "invalid_discount_offer_type",
                "email_not_opted_in",
            ]
        ):
            policy_violations += 1

        # ---------------------------------------------------------
        # Unsafe customer messages
        # ---------------------------------------------------------
        if any(
            flag.startswith(
                "unsafe_message_phrase:"
            )
            for flag in actual.risk_flags
        ):
            unsafe_messages += 1

    return EvaluationReport(
        total_cases=len(EXPECTED_BEHAVIOR),
        correct_decisions=correct_decisions,
        correct_offers=correct_offers,
        correct_discounts=correct_discounts,
        policy_violations=policy_violations,
        unsafe_messages=unsafe_messages,
    )


def print_report(
    report: EvaluationReport,
) -> None:

    print("\n" + "=" * 50)
    print("CART WIN-BACK AGENT EVALUATION")
    print("=" * 50)

    print(
        f"Decision accuracy: "
        f"{report.decision_accuracy:.1%}"
    )

    print(
        f"Offer accuracy: "
        f"{report.offer_accuracy:.1%}"
    )

    print(
        f"Discount accuracy: "
        f"{report.discount_accuracy:.1%}"
    )

    print(
        f"Policy violations: "
        f"{report.policy_violations}"
    )

    print(
        f"Unsafe messages detected: "
        f"{report.unsafe_messages}"
    )

    print("=" * 50)