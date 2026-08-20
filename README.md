# Seattle Seawolves Cart Win-Back AI

> An agentic AI decision system for abandoned-cart recovery where **AI reasons, deterministic code enforces, and humans approve**.

---

## Table of Contents

- [Screenshots](#screenshots)
- [Challenge Submission](#challenge-submission)
  - [Section A — Written Analysis](#section-a--written-analysis)
  - [Section B — Agent Quality & Failure Plan](#section-b--agent-quality--failure-plan)
  - [Section C — AI Usage Log](#section-c--ai-usage-log)
- [Overview](#overview)
- [Problem](#problem)
- [Architecture](#architecture)
- [Core Principle](#core-principle)
- [Workflow](#workflow)
- [Agents and Governance](#agents-and-governance)
- [Technology Stack](#technology-stack)
- [API](#api)
- [Evaluation](#evaluation)
- [Project Structure](#project-structure)
- [Engineering Principles](#engineering-principles)
- [Limitations and Future Improvements](#limitations-and-future-improvements)
- [Recruiter Takeaway](#recruiter-takeaway)

---

## Screenshots

### Marketer Dashboard

![Marketer Dashboard](screenshots/03-marketer-dashboard.png)

### Evaluation Results

![Evaluation Results](screenshots/01-evaluation-results.png)

### Automated Tests

![Automated Test Results](screenshots/02-test-results.png)

### FastAPI / OpenAPI Documentation

![FastAPI OpenAPI Documentation](screenshots/04-api-documentation.png)

### Structured API Response

![Structured API Response](screenshots/05-api-response.png)

---

# Challenge Submission

## Section A — Written Analysis

The goal was to make the first version useful to a marketer within one sprint without building a full CRM or personalization platform. I therefore scoped the system around one decision: whether a stale cart deserves a win-back intervention and, if so, what the marketer should send.

The agent first evaluates cart and fan context through an Eligibility Agent. Signals include how long the cart has been abandoned, cart value, previous ticket history, recency of the last purchase, and email opt-in status. Eligible carts are then passed to an Offer Strategy Agent, which selects a focused strategy: a reminder, a first-purchase incentive, or no action. This separation keeps eligibility and offer selection as distinct reasoning steps rather than one large prompt.

The system deliberately does not assume that every abandoned cart deserves a discount. A reminder can be preferable when a fan is already engaged, while a first-purchase incentive can be appropriate for a fan with no ticket history. A cart can also result in `no_action` when the available signals do not justify contacting the fan.

The LLM only proposes a recommendation. Deterministic application code enforces business constraints such as allowed actions and discount limits. Customer-facing messaging then passes through validation and a safety gate before the recommendation reaches the marketer. This matters because a wrong offer can cost both revenue and fan trust.

For the one-sprint scope, I deliberately did not build CRM integration, automated email/SMS delivery, cross-team personalization, long-term customer segmentation, production-scale experimentation, or a six-team/leagues-wide marketing engine. The shipped proof of concept instead gives one marketer a usable review surface where recommendations can be inspected, edited, approved, or rejected before any fan-facing action.

## Section B — Agent Quality & Failure Plan

The agent is evaluated against explicit expected decisions rather than only checking whether it runs successfully.

Current evaluation:

| Metric | Result |
|---|---:|
| Decision Accuracy | **100%** |
| Offer Accuracy | **100%** |
| Discount Accuracy | **100%** |
| Policy Violations | **0** |
| Unsafe Message Flags | **0** |
| Automated Tests | **7 passed** |

The current five-cart test set expects:

```text
C-1001 -> reminder
C-1002 -> 5% first_purchase
C-1003 -> no_action
C-1004 -> reminder
C-1005 -> no_action
```

A key failure mode is an LLM producing a plausible but financially incorrect offer. For example, the model could recommend a 20% discount when the business policy allows a maximum of 10%. The deterministic policy engine catches this independently of the model and rejects or corrects the recommendation before it can reach a fan.

Another failure mode is a reasonable strategy paired with an inappropriate customer-facing message. The message validator and safety gate provide another control point before marketer review.

The five-cart evaluation is intentionally treated as a proof-of-concept baseline, not evidence of production-level generalization. Before launch, I would expand the dataset, add adversarial and edge-case scenarios, run regression evaluation in CI/CD, and monitor policy violations, recommendation overrides, and downstream outcomes.

## Section C — AI Usage Log

AI was used as an engineering collaborator rather than as an unquestioned implementation authority.

### Interaction 1 — Architecture

**Asked AI to help with:** Designing an agentic architecture for cart win-back.

**AI output:** A workflow separating cart eligibility and offer strategy.

**Kept:** The separation of responsibilities.

**Changed:** Added deterministic policy enforcement, safety validation, and human approval around the AI-generated recommendation.

**Why:** The challenge explicitly involves real revenue and fan-trust risk, so business-critical constraints should not depend entirely on probabilistic model output.

### Interaction 2 — Offer Logic

**Asked AI to help with:** Designing recommendation logic for reminder, incentive, and no-action outcomes.

**AI output:** A recommendation flow that could turn eligible carts into offers.

**Kept:** The multi-step strategy approach.

**Changed:** Preserved `no_action` as a valid outcome instead of forcing every stale cart into an offer.

**Why:** The challenge explicitly says deciding which carts are worth acting on is part of the task.

### Interaction 3 — Validation and Evaluation

**Asked AI to help with:** Making the system testable and safe around model-generated recommendations.

**AI output:** Suggestions for structured outputs, validation, and explicit expected decisions.

**Kept:** Structured recommendations and automated evaluation.

**Changed:** Added deterministic policy checks and separate safety/message validation rather than treating the LLM response as the final action.

**Why:** A system can produce output that looks reasonable while still violating a financial or messaging constraint.


# Overview

**Seattle Seawolves Cart Win-Back AI** is an AI-assisted cart recovery decision system designed to determine the most appropriate action for an abandoned cart.

It combines:

- LLM-based reasoning
- Multi-agent architecture
- Structured AI outputs
- Deterministic business rules
- Policy enforcement
- Safety validation
- Human-in-the-loop approval
- Automated evaluation
- FastAPI
- Next.js

> **AI reasons. Deterministic code enforces. Humans approve.**

---

# Problem

Every abandoned cart should not automatically receive a discount.

The system needs to determine:

- Whether the cart is eligible
- Whether to send a reminder
- Whether an incentive is justified
- What offer is allowed
- Whether the message is safe
- Whether the recommendation complies with policy
- Whether a human should review it

The project separates **probabilistic AI reasoning** from **deterministic business enforcement**.

---

# Architecture

```text
Cart / Customer Context
          |
          v
   Eligibility Agent
          |
          v
  Offer Strategy Agent
          |
          v
  Structured AI Output
          |
          v
 Deterministic Policy
       Engine
          |
          v
  Message Validator
          |
          v
      Safety Gate
          |
          v
     Marketer UI
          |
          v
    Human Approval
          |
          v
    Business Action
```

## Core Principle

### AI Reasons

LLMs handle contextual reasoning and recommendation generation.

### Deterministic Code Enforces

Application code controls:

- Eligibility constraints
- Allowed actions
- Discount limits
- Business policies
- Validation
- Safety constraints

### Humans Approve

Recommendations are presented to a marketer before business-critical execution.

---

# Workflow

```text
1. Cart enters system
2. Eligibility is evaluated
3. Offer strategy is generated
4. Structured recommendation is produced
5. Policy rules are enforced
6. Message is validated
7. Safety checks are applied
8. Recommendation is presented to marketer
9. Human approves or rejects
```

The LLM never directly controls the final business action.

---

# Agents and Governance

## Eligibility Agent

Determines whether a cart qualifies for a win-back intervention.

## Offer Strategy Agent

Selects an appropriate strategy:

- `reminder`
- `first_purchase`
- `no_action`

## Deterministic Policy Engine

Validates AI recommendations against business rules.

For example:

```text
AI recommends 20% discount
          |
          v
Policy Engine
          |
          v
Maximum allowed = 10%
          |
          v
Reject / Correct
```

## Message Validator

Ensures customer-facing messaging matches the selected action and passes validation.

## Safety Gate

Blocks unsafe or inappropriate customer-facing content.

## Human-in-the-Loop

Keeps business actions under human control.

---

# Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Frontend | Next.js |
| AI | LLMs |
| Architecture | Multi-agent |
| Outputs | Structured AI outputs |
| Governance | Deterministic policy engine |
| Safety | Message validation + safety gate |
| API | REST |
| Evaluation | Automated evaluation |
| Workflow | Human-in-the-loop |

---

# API

Backend:

```text
http://127.0.0.1:8000
```

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/carts` | Retrieve cart data |
| GET | `/recommendations` | Retrieve validated recommendations |

Interactive API documentation is available through FastAPI/OpenAPI when the backend is running.

Frontend:

```text
http://localhost:3000
```

---

# Evaluation

The project includes a dedicated evaluation workflow using:

```text
backend/evaluation/
├── expected_decisions.py
├── evaluator.py
└── run_evaluation.py
```

The evaluation measures:

- Decision accuracy
- Offer accuracy
- Discount accuracy
- Policy violations
- Unsafe-message flags

## Current Results

| Metric | Result |
|---|---:|
| Decision Accuracy | **100%** |
| Offer Accuracy | **100%** |
| Discount Accuracy | **100%** |
| Policy Violations | **0** |
| Unsafe Message Flags | **0** |
| Test Suite | **7 passed** |

### Evaluated Carts

| Cart | Recommendation |
|---|---|
| C-1001 | reminder |
| C-1002 | 5% first_purchase |
| C-1003 | no_action |
| C-1004 | reminder |
| C-1005 | no_action |

> Results are based on the current five-cart evaluation set and should not be interpreted as production-level generalization.

---

# Project Structure

```text
seawolves-cart-winback/
|
+-- backend/
|   +-- app/
|   |   +-- agents/
|   |   +-- api/
|   |   +-- models/
|   |   +-- policies/
|   |   +-- services/
|   |
|   +-- evaluation/
|   +-- tests/
|
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- lib/
|
+-- data/
+-- docs/
+-- screenshots/
+-- README.md
+-- requirements.txt
+-- .gitignore
```

---

# Engineering Principles

## Separation of Concerns

Reasoning, policy, safety, API serving, frontend presentation, and evaluation are separated.

## Deterministic Control

Business-critical rules are enforced outside the LLM.

## Structured Outputs

AI responses are structured so application code can validate and consume them reliably.

## Fail-Safe Behavior

Invalid or policy-violating AI recommendations should not become executable business actions.

## Evaluation-First

Expected decisions and automated metrics make the system measurable and regression-testable.

---

# Limitations and Future Improvements

The current evaluation uses five carts. A production system would require broader testing and operational controls.

Future improvements include:

- Larger evaluation datasets
- Adversarial and edge-case testing
- CI/CD regression evaluation
- Authentication and authorization
- Persistent storage
- Observability and monitoring
- Policy versioning and audit trails
- Human feedback loops
- A/B testing
- Production deployment infrastructure

---

# Recruiter Takeaway

This project demonstrates practical AI engineering rather than simply wrapping an LLM API.

The key architecture is:

```text
AI Reasoning
     +
Structured Decisions
     +
Deterministic Policy
     +
Safety Validation
     +
Human Approval
     +
Automated Evaluation
     =
Controlled AI System
```

The strongest engineering principle is the separation between **probabilistic intelligence** and **deterministic control**.

The LLM provides reasoning and recommendations.

The application determines what is actually allowed.

The human remains in control of the final business action.

---

# Conclusion

Seattle Seawolves Cart Win-Back AI demonstrates how agentic AI can be integrated into a business workflow while maintaining validation, safety, policy enforcement, measurable evaluation, and human oversight.

> **AI reasons. Deterministic code enforces. Humans approve.**
