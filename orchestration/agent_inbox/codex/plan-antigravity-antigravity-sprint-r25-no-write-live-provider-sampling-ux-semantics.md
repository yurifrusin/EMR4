# plan-antigravity-antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r25-no-write-live-provider-sampling-ux-semantics` |
| Status | integrated |
| Created | 2026-07-05 23:46 +1000 |
| Source HEAD | `1d6183d` |

## Plan Summary

Define product and receptionist semantics for a default-disabled, no-write live-provider sampling harness in docs/receptionist_review_r25.md.

## My Understanding

EMR4 is introducing a default-disabled, no-write live-provider sampling harness. In this plan-only sprint, we will draft the product and receptionist-facing semantics for this harness, covering evidence labels, staff copy, cost/latency expectations, and criteria for declaring readiness unproven.

## Intended Surface / Boundary

Only the new documentation file docs/receptionist_review_r25.md. No production code, tests, or UI files will be edited.

## Out Of Scope

Writing Python/JS code, making live Vertex/Gemini calls, database migrations, changing prompt files, or modifying credentials.

## Files I Expect To Edit

docs/receptionist_review_r25.md

## Implementation Steps

1. Draft the outline of docs/receptionist_review_r25.md. 2. Define clear evidence labels (e.g. live_provider: true) to distinguish sampled live runs. 3. Formulate staff copy guidelines to ensure non-authoritative tone and transparency. 4. Detail cost/latency budgets and expectations. 5. Establish exact criteria for declaring live-provider readiness unproven. 6. Review draft against R24 guidelines.

## Visual / Behavioural Acceptance Checks

1. docs/receptionist_review_r25.md exists. 2. No changes in app/, tests/, docs/diary/. 3. The document covers evidence labels, staff copy, cost/latency, and unproven readiness.

## Risks / Ambiguities

Live-model behavior is non-deterministic; the plan mitigates this by defining objective threshold-based metrics for unproven readiness.

## Codex Plan Review

- Review result: Accepted with Ariadne integration cleanup.
- Required changes before implementation: narrow "live-provider" language to R25's actual static, default-disabled scaffold; keep live shadow sampling as future gated work.
- Approved to proceed: yes; completed and integrated in Sprint R25.
