from app.services.orchestrator import WinBackOrchestrator
from app.services.data_service import load_carts

from evaluation.evaluator import (
    evaluate_recommendations,
    print_report,
)


def main():
    print("Running cart win-back evaluation...")

    # ---------------------------------------------------------
    # Step 1:
    # Load the supplied stale-cart dataset.
    # ---------------------------------------------------------
    carts = load_carts()

    print(
        f"Loaded {len(carts)} carts."
    )

    # ---------------------------------------------------------
    # Step 2:
    # Run the complete agentic workflow.
    #
    # Cart
    #   ↓
    # Eligibility Agent
    #   ↓
    # Offer Strategy Agent
    #   ↓
    # Policy Engine
    #   ↓
    # Message Validator
    #   ↓
    # Safety Gate
    # ---------------------------------------------------------
    orchestrator = WinBackOrchestrator()

    recommendations = orchestrator.process_carts(
        carts
    )

    # ---------------------------------------------------------
    # Step 3:
    # Evaluate the generated recommendations against
    # our expected business behavior.
    # ---------------------------------------------------------
    report = evaluate_recommendations(
        recommendations
    )

    # ---------------------------------------------------------
    # Step 4:
    # Print the evaluation report.
    # ---------------------------------------------------------
    print_report(report)


if __name__ == "__main__":
    main()