# Seattle Seawolves Cart Win-Back AI

> An agentic AI decision system for abandoned-cart recovery where **AI reasons, deterministic code enforces, and humans approve**.

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Project Objective](#project-objective)
- [Core Architectural Principle](#core-architectural-principle)
- [Why This Is More Than an LLM Wrapper](#why-this-is-more-than-an-llm-wrapper)
- [System Architecture](#system-architecture)
- [End-to-End Workflow](#end-to-end-workflow)
- [Multi-Agent Design](#multi-agent-design)
- [Deterministic Policy Engine](#deterministic-policy-engine)
- [Message Validation and Safety](#message-validation-and-safety)
- [Human-in-the-Loop](#human-in-the-loop)
- [Decision Model](#decision-model)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Backend API](#backend-api)
- [Frontend](#frontend)
- [Evaluation](#evaluation)
- [Evaluation Results](#evaluation-results)
- [Engineering Principles](#engineering-principles)
- [Why Not Let the LLM Decide Everything?](#why-not-let-the-llm-decide-everything)
- [Example Decision Flow](#example-decision-flow)
- [Reproducibility](#reproducibility)
- [Security and AI Governance](#security-and-ai-governance)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Recruiter Takeaway](#recruiter-takeaway)
- [Interview Explanation](#interview-explanation)
- [Conclusion](#conclusion)

---

## Overview

**Seattle Seawolves Cart Win-Back AI** is an AI-assisted cart recovery decision system designed to determine the most appropriate action for an abandoned shopping cart.

The system does not simply send every customer a discount.

Instead, it combines:

- LLM-based reasoning
- Multi-agent architecture
- Structured AI outputs
- Deterministic business rules
- Policy enforcement
- Message validation
- Safety checks
- Human-in-the-loop approval
- Automated evaluation
- FastAPI backend
- Next.js marketer interface

The system is designed around one central architectural principle:

> **AI reasons. Deterministic code enforces. Humans approve.**

---

## The Problem

Cart abandonment is not a simple binary problem where every abandoned cart should receive a discount.

A practical win-back system needs to answer questions such as:

1. Is this customer actually eligible for a win-back intervention?
2. Should the customer receive a reminder?
3. Is an incentive justified?
4. If an incentive is justified, what type should it be?
5. What discount is allowed?
6. Is the generated customer message appropriate?
7. Does the recommendation comply with business policy?
8. Should the system take no action?
9. Should a marketer review the recommendation before execution?

A system that gives an LLM unrestricted control over these decisions can produce inconsistent or invalid outcomes.

This project addresses that problem by separating **reasoning** from **enforcement**.

---

## Project Objective

The objective is to build an end-to-end AI decision-support workflow that can:

1. Analyze cart and customer context.
2. Determine eligibility.
3. Generate a structured recommendation.
4. Select an appropriate win-back strategy.
5. Validate the recommendation against deterministic business policies.
6. Validate customer-facing messaging.
7. Apply safety checks.
8. Present the final recommendation through an API and marketer interface.
9. Measure correctness through automated evaluation.

The goal is not to maximize the number of discounts.

The goal is to make the **best policy-compliant decision for each cart**.

---

# Core Architectural Principle

## AI Reasons. Deterministic Code Enforces. Humans Approve.

This is the most important architectural decision in the project.

### AI Reasons

The AI layer is useful for tasks that benefit from contextual reasoning, such as:

- Understanding customer/cart context
- Determining whether intervention may be useful
- Selecting a strategy
- Generating a recommendation
- Producing structured reasoning-oriented outputs

### Deterministic Code Enforces

Business-critical rules are not delegated entirely to the LLM.

Deterministic application code handles:

- Eligibility constraints
- Allowed actions
- Discount limits
- Business policies
- Validation
- Safety constraints
- Final decision enforcement

### Humans Approve

The system is designed as decision support rather than unrestricted autonomous execution.

A marketer can review the recommendation before a business action is taken.

This creates a controlled workflow:

```text
AI Recommendation
       |
       v
Deterministic Policy Validation
       |
       v
Message Validation
       |
       v
Safety Gate
       |
       v
Human Review / Approval
       |
       v
Business Action
```

---

# Why This Is More Than an LLM Wrapper

A simple LLM wrapper usually looks like:

```text
User Input
    |
    v
LLM
    |
    v
Text Response
```

This project is fundamentally different.

The architecture contains separate reasoning, governance, validation, application, and evaluation layers:

```text
                    +----------------------+
                    |   Cart / Customer    |
                    |       Context       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Eligibility Agent  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Offer Strategy Agent |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Structured AI Output |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Deterministic Policy |
                    |       Engine         |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Message Validator   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |     Safety Gate      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    Marketer UI       |
                    |   Human Approval     |
                    +----------+-----------+
                               |
                               v
                         Final Action
```

This demonstrates practical AI engineering rather than simply calling an LLM API.

---

# System Architecture

The system consists of the following major components.

## 1. Eligibility Agent

Determines whether a cart/customer is eligible for a win-back intervention.

Responsibilities:

- Analyze cart context
- Evaluate eligibility conditions
- Determine whether intervention is appropriate
- Produce a structured eligibility decision

---

## 2. Offer Strategy Agent

Determines what strategy should be used for an eligible cart.

Possible strategies include:

- Reminder
- First-purchase incentive
- No action

The agent is responsible for contextual strategy selection rather than directly executing a business action.

---

## 3. Structured AI Output

AI responses are represented in structured forms rather than relying on unrestricted natural-language output.

This provides:

- Predictable downstream behavior
- Easier validation
- Better integration with application code
- Reduced ambiguity
- Easier testing
- More reliable agent-to-agent communication

---

## 4. Deterministic Policy Engine

The policy engine is one of the most important components of the architecture.

It validates the AI recommendation against deterministic business rules.

For example:

```text
AI recommends 20% discount
           |
           v
Policy Engine
           |
           v
Maximum allowed discount = 10%
           |
           v
Recommendation rejected or corrected
```

The LLM cannot bypass this layer.

The policy engine acts as the deterministic authority over business constraints.

---

## 5. Message Validator

The message validator checks the customer-facing communication.

It ensures that:

- The message corresponds to the selected action
- The message is consistent with the recommendation
- Invalid messaging is rejected
- Customer-facing output passes validation before reaching the final workflow

---

## 6. Safety Gate

The safety gate provides an additional control layer before the recommendation is presented for execution.

Its purpose is to detect and block:

- Unsafe messaging
- Inappropriate content
- Invalid customer-facing outputs

This makes safety a dedicated system component rather than an assumption inside a prompt.

---

## 7. Marketer UI

The frontend provides a human-facing interface where recommendations can be reviewed.

The UI is designed around the idea that AI should assist the marketer rather than silently execute business-critical actions.

---

## 8. Evaluation System

The project includes an explicit evaluation workflow.

Important files include:

```text
expected_decisions.py
evaluator.py
run_evaluation.py
```

The evaluator compares actual system behavior against expected decisions and calculates measurable outcomes.

---

# End-to-End Workflow

The complete decision pipeline is:

```text
1. Cart enters the system
          |
          v
2. Customer/cart context is analyzed
          |
          v
3. Eligibility Agent
          |
          v
4. Offer Strategy Agent
          |
          v
5. Structured recommendation generated
          |
          v
6. Deterministic Policy Engine
          |
          v
7. Message Validator
          |
          v
8. Safety Gate
          |
          v
9. Final recommendation
          |
          v
10. Marketer review
          |
          v
11. Approved business action
```

The important point is that the LLM does not directly control the final action.

---

# Multi-Agent Design

The system uses multiple specialized reasoning components instead of placing all responsibility inside one large prompt.

## Why Multiple Agents?

Different decisions represent different responsibilities.

For example:

```text
Eligibility
     |
     v
Strategy
     |
     v
Validation
     |
     v
Execution
```

Separating these responsibilities provides:

- Smaller reasoning scopes
- Easier testing
- Easier debugging
- Better separation of concerns
- Replaceable components
- More transparent system behavior

## Eligibility Agent

The Eligibility Agent answers:

> "Should this cart be considered for a win-back intervention?"

It focuses on eligibility rather than deciding the entire business workflow.

## Offer Strategy Agent

The Offer Strategy Agent answers:

> "Given that this cart can receive an intervention, what is the appropriate strategy?"

It can recommend:

- Reminder
- Incentive
- No action

---

# Deterministic Policy Engine

The policy engine is responsible for enforcing rules that should not depend on probabilistic model behavior.

Examples of deterministic constraints include:

```text
Allowed action types
Maximum discount
Eligibility requirements
Required conditions
Message constraints
Safety requirements
```

A conceptual policy flow is:

```text
AI Recommendation
       |
       v
Is action allowed?
       |
      Yes
       |
       v
Is discount within limits?
       |
      Yes
       |
       v
Does recommendation satisfy business policy?
       |
      Yes
       |
       v
Continue
```

If a recommendation fails validation:

```text
AI Recommendation
       |
       v
Policy Violation
       |
       v
Reject / Correct
       |
       v
Do Not Execute
```

This provides deterministic control around a probabilistic AI layer.

---

# Message Validation and Safety

A recommendation can be logically correct but still produce an inappropriate customer-facing message.

Therefore, messaging is treated as its own validation stage.

```text
Recommendation
      |
      v
Message Generation
      |
      v
Message Validator
      |
      v
Safety Gate
      |
      v
Approved Output
```

This layered approach makes it easier to identify whether a failure originated from:

- Reasoning
- Strategy
- Policy
- Messaging
- Safety

---

# Human-in-the-Loop

The system intentionally retains human oversight.

The workflow is:

```text
AI
 |
 v
Recommendation
 |
 v
Validation
 |
 v
Marketer
 |
 +---- Approve ----> Action
 |
 +---- Reject -----> No Action / Revision
```

This is especially useful for business workflows where recommendations can have financial, customer-experience, or brand implications.

The system therefore follows a **human-in-the-loop** rather than an unrestricted autonomous-agent model.

---

# Decision Model

The system supports three important classes of outcomes.

## Reminder

A non-discount recovery message is recommended.

```text
Action = reminder
```

This allows the system to attempt recovery without immediately sacrificing margin.

## First-Purchase Incentive

A controlled incentive can be recommended when the customer/cart satisfies the relevant conditions.

Example:

```text
Action = first_purchase
Discount = 5%
```

The exact incentive remains subject to deterministic policy enforcement.

## No Action

No action is a valid decision.

```text
Action = no_action
```

This is an important design choice.

The system is not optimized to force an intervention on every cart.

Instead:

> **The correct action can be to do nothing.**

This avoids treating discounts as the default solution to every abandoned cart.

---

# Technology Stack

| Layer | Technology / Concept |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Frontend | Next.js |
| AI | LLM-based reasoning |
| Architecture | Multi-agent system |
| AI Outputs | Structured outputs |
| Governance | Deterministic policy engine |
| Safety | Message validation and safety gate |
| API | REST |
| Evaluation | Automated evaluation framework |
| Workflow | Human-in-the-loop |

---

# Project Structure

A logical representation of the project is:

```text
seawolves-cart-winback/
|
+-- agents/
|   +-- eligibility/
|   +-- offer_strategy/
|
+-- policy/
|   +-- deterministic_rules
|
+-- validation/
|   +-- message_validator
|   +-- safety_gate
|
+-- backend/
|   +-- FastAPI application
|
+-- frontend/
|   +-- Next.js application
|
+-- evaluation/
|   +-- expected_decisions.py
|   +-- evaluator.py
|   +-- run_evaluation.py
|
+-- README.md
```

The exact physical structure can evolve, but the architectural separation remains important.

---

# Backend API

The backend runs on:

```text
http://127.0.0.1:8000
```

## Health Check

```http
GET /health
```

Purpose:

- Verify backend availability
- Provide a simple health endpoint

## Carts

```http
GET /carts
```

Purpose:

- Retrieve cart information
- Provide cart context to the application

## Recommendations

```http
GET /recommendations
```

Purpose:

- Retrieve generated and validated win-back recommendations
- Provide recommendation data to the frontend

---

# Frontend

The marketer interface runs on:

```text
http://localhost:3000
```

The frontend provides a human-facing view of the AI decision workflow.

The intended experience is:

```text
Cart
 |
 v
Recommendation
 |
 +--> Strategy
 |
 +--> Offer
 |
 +--> Validation Status
 |
 +--> Safety Status
 |
 v
Marketer Review
```

This makes the AI decision visible instead of hiding it behind an automated process.

---

# Evaluation

A dedicated evaluation layer was implemented to test whether the system makes the expected decisions.

Important evaluation files:

```text
expected_decisions.py
evaluator.py
run_evaluation.py
```

The evaluation checks:

- Decision accuracy
- Offer accuracy
- Discount accuracy
- Policy violations
- Unsafe-message flags

This is important because an AI system should not be evaluated only by looking at whether the output "sounds good."

It should be evaluated against explicit expected behavior.

---

# Evaluation Results

The current evaluation contains:

```text
5 test carts
```

Current results:

| Metric | Result |
|---|---:|
| Decision Accuracy | 100% |
| Offer Accuracy | 100% |
| Discount Accuracy | 100% |
| Policy Violations | 0 |
| Unsafe Message Flags | 0 |

## Test Results

| Cart | Expected / Observed Recommendation |
|---|---|
| C-1001 | reminder |
| C-1002 | 5% first_purchase |
| C-1003 | no_action |
| C-1004 | reminder |
| C-1005 | no_action |

The current test suite demonstrates complete agreement with the expected decisions across the five evaluated carts.

---

# What These Results Mean

The evaluation demonstrates that, on the current test set:

- The system selected the expected decision for every cart.
- The selected offer matched the expected offer.
- The discount matched the expected discount.
- No policy violations were detected.
- No unsafe-message flags were detected.

These results are intentionally reported as **current evaluation results**, not as a claim of production-level generalization.

A larger evaluation dataset would be required to establish robustness across real-world conditions.

---

# Engineering Principles

## 1. Separation of Concerns

Reasoning, policy, safety, API serving, frontend presentation, and evaluation are separate responsibilities.

This makes the system easier to:

- Understand
- Test
- Debug
- Extend
- Replace

## 2. Deterministic Control

Business-critical constraints are enforced through application code.

The LLM does not become the source of truth for business policy.

## 3. Structured AI Outputs

AI outputs are structured so that downstream components can validate and consume them reliably.

This reduces the risk associated with unrestricted natural-language output.

## 4. Human Oversight

The system treats AI recommendations as decision support.

Humans retain control over business actions.

## 5. Evaluation-First Thinking

The project defines expected decisions and measures actual results.

This creates a foundation for:

- Regression testing
- Model comparison
- Prompt evaluation
- Policy testing
- Continuous improvement

## 6. Fail-Safe Behavior

A recommendation that fails policy or safety validation should not become an executable action.

Conceptually:

```text
Invalid AI Output
       |
       v
Validation Failure
       |
       v
Block
       |
       v
No Business Action
```

---

# Why Not Let the LLM Decide Everything?

LLMs are powerful reasoning systems, but they are probabilistic.

Business rules often need deterministic guarantees.

For example, suppose the policy says:

```text
Maximum allowed discount = 10%
```

An LLM might generate:

```text
Offer the customer 20% off.
```

The correct architecture is not:

```text
LLM
 |
 v
20% Discount
 |
 v
Execute
```

Instead:

```text
LLM
 |
 v
20% Recommendation
 |
 v
Policy Engine
 |
 v
Rejected
 |
 v
No Execution
```

This is the key distinction between using AI as a reasoning component and allowing AI to become an uncontrolled business execution layer.

---

# Example Decision Flow

Consider an abandoned cart.

## Step 1: Context

The system receives cart/customer information.

```text
Cart ID: C-1002
Status: Abandoned
```

## Step 2: Eligibility

The Eligibility Agent determines that the cart qualifies for intervention.

```text
Eligible: true
```

## Step 3: Strategy

The Offer Strategy Agent recommends:

```text
Strategy: first_purchase
Discount: 5%
```

## Step 4: Policy Validation

The deterministic policy engine checks:

```text
Is first_purchase allowed?
Is 5% within the permitted range?
Does the customer satisfy the required conditions?
```

If all checks pass:

```text
Policy Status: Approved
```

## Step 5: Message Validation

The customer-facing message is checked for consistency and validity.

## Step 6: Safety Gate

The final message passes the safety layer.

## Step 7: Human Review

The marketer sees the recommendation and can approve it.

## Final Decision

```text
C-1002
Action: first_purchase
Discount: 5%
Status: Validated
```

---

# Reproducibility

## Backend

Start the FastAPI application using the project environment.

Expected address:

```text
http://127.0.0.1:8000
```

Verify:

```http
GET /health
```

## Frontend

Start the Next.js application.

Expected address:

```text
http://localhost:3000
```

## Evaluation

Run the evaluation workflow using:

```text
expected_decisions.py
evaluator.py
run_evaluation.py
```

The current expected evaluation outcome is:

```text
Decision Accuracy: 100%
Offer Accuracy: 100%
Discount Accuracy: 100%
Policy Violations: 0
Unsafe Message Flags: 0
```

---

# Security and AI Governance

Although this is a project implementation rather than a full production deployment, the architecture incorporates several important AI governance concepts.

## Policy Enforcement

Business constraints are enforced outside the LLM.

## Safety Validation

Customer-facing output passes through a dedicated safety layer.

## Structured Outputs

AI responses are constrained into predictable formats.

## Human Approval

Business actions can remain subject to human review.

## Evaluation

The system measures correctness instead of relying solely on qualitative inspection.

## Auditability

Separating reasoning from enforcement makes it easier to understand why a recommendation was produced and whether it was accepted or rejected by policy.

---

# Current Limitations

The current evaluation uses a small five-cart test set.

Therefore:

> The reported 100% accuracy demonstrates correctness on the current evaluation cases, not guaranteed production-level performance.

A production system would require significantly broader validation.

Additional considerations include:

- Larger evaluation datasets
- Real-world customer variability
- Adversarial inputs
- Edge cases
- Model failures
- Prompt injection resistance
- Authentication
- Authorization
- Persistent storage
- Monitoring
- Observability
- Rate limiting
- Production logging
- Privacy controls
- Audit trails
- Business-specific compliance requirements

---

# Future Improvements

Potential next steps include:

## Evaluation

- Expand the test dataset
- Add adversarial cases
- Add edge-case scenarios
- Add regression tests
- Add automated evaluation to CI/CD
- Compare multiple model versions

## AI

- Improve agent reasoning
- Add model/version tracking
- Add confidence signals
- Add human feedback loops
- Evaluate recommendation quality over time

## Backend

- Add authentication
- Add authorization
- Add persistent database storage
- Add asynchronous processing
- Add structured logging
- Add API rate limiting

## Governance

- Add policy versioning
- Add detailed audit trails
- Add approval history
- Add explainability metadata
- Add policy simulation before deployment

## Production

- Add monitoring
- Add alerting
- Add observability
- Add A/B testing
- Add experiment tracking
- Add production-grade deployment infrastructure

---

# Recruiter Takeaway

This project demonstrates practical AI engineering across multiple layers of a real application.

It is not simply:

```text
Prompt -> LLM -> Response
```

It is:

```text
Context
   |
   v
AI Reasoning
   |
   v
Structured Decision
   |
   v
Deterministic Policy
   |
   v
Safety Validation
   |
   v
Human Review
   |
   v
Business Action
```

The strongest engineering signal is the architectural boundary between **probabilistic intelligence** and **deterministic control**.

The LLM provides reasoning and recommendations.

The application decides what is actually allowed.

The human remains in control of the final business action.

---

# Skills Demonstrated

## Programming and Backend

- Python
- FastAPI
- REST APIs
- Backend architecture
- Structured data validation

## AI and Agentic Engineering

- LLM integration
- Agentic AI
- Multi-agent systems
- Structured LLM outputs
- AI-assisted decision making

## AI Governance

- Deterministic policy enforcement
- Safety validation
- Human-in-the-loop systems
- Automated evaluation
- Fail-safe AI workflows

## Software Engineering

- Separation of concerns
- Modular architecture
- API design
- Validation
- Testing
- Evaluation
- Error containment

## Frontend

- Next.js
- AI decision presentation
- Marketer-facing workflow

---

# Interview Explanation

If asked:

> **"Tell me about this project."**

A strong explanation is:

> I built an AI-assisted cart win-back decision system around the principle that AI should reason, deterministic code should enforce, and humans should approve. Instead of allowing an LLM to directly decide and execute discounts, I separated the workflow into an Eligibility Agent and an Offer Strategy Agent. Their structured recommendations pass through a deterministic policy engine, message validation, and a safety gate before being presented to a marketer through a FastAPI backend and Next.js interface. I also built an evaluation layer with expected decisions and automated metrics. On the current five-cart test set, the system achieved 100% decision, offer, and discount accuracy with zero policy violations and zero unsafe-message flags.

## If Asked: "Why Did You Use Multiple Agents?"

> I separated eligibility from offer strategy because they represent different responsibilities. The Eligibility Agent determines whether an intervention is appropriate, while the Offer Strategy Agent determines what type of intervention should be used. This makes the system easier to test, debug, replace, and extend than putting all reasoning into a single prompt.

## If Asked: "Why Not Just Ask the LLM for the Discount?"

> Because business-critical rules should not depend entirely on probabilistic model behavior. The LLM can recommend an action, but the deterministic policy engine decides whether that recommendation is actually allowed. For example, if the model recommends a discount above the business limit, the policy engine rejects it. This gives us the flexibility of AI reasoning while maintaining deterministic control.

## If Asked: "What Is the Most Important Design Decision?"

> The most important design decision is separating AI reasoning from business enforcement. The LLM is treated as a reasoning component rather than the final authority. This makes the system safer, more testable, and more auditable.

## If Asked: "What Happens If the AI Gives a Bad Recommendation?"

> The recommendation does not go directly to execution. It passes through deterministic policy validation, message validation, and a safety gate. If it violates a rule or safety constraint, the recommendation can be rejected or prevented from becoming an executable business action.

## If Asked: "How Did You Evaluate the System?"

> I created explicit expected decisions and an evaluation workflow. The evaluator compares the actual recommendations against those expected decisions and measures decision accuracy, offer accuracy, discount accuracy, policy violations, and unsafe-message flags. On the current five-cart evaluation set, all decision, offer, and discount metrics were 100%, with zero policy violations and zero unsafe-message flags.

---

# What This Project Shows

This project demonstrates an understanding of an important principle in modern AI systems:

> **Good AI engineering is not just about making models generate better answers. It is about designing reliable systems around those models.**

The architecture addresses:

```text
Reasoning
    +
Validation
    +
Policy
    +
Safety
    +
Human Oversight
    +
Evaluation
    =
Controlled AI System
```

That is the core engineering value of the project.

---

# Conclusion

Seattle Seawolves Cart Win-Back AI demonstrates how an LLM can be integrated into a real business workflow without giving the model unrestricted control.

The project combines:

- Agentic reasoning
- Multi-agent architecture
- Structured AI outputs
- Deterministic policy enforcement
- Safety validation
- Human-in-the-loop approval
- Automated evaluation
- FastAPI
- Next.js
- API-driven architecture

The central principle remains:

> **AI reasons. Deterministic code enforces. Humans approve.**

This architecture provides a practical foundation for building AI systems that are not only intelligent, but also **controlled, testable, explainable, and suitable for real-world business workflows**.
