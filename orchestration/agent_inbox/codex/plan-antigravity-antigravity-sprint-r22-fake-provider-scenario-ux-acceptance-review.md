# plan-antigravity-antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r22-fake-provider-scenario-ux-acceptance-review` |
| Status | pending_plan_review |
| Created | 2026-07-05 22:30 +1000 |
| Source HEAD | `ab798a9` |

## Plan Summary

Define receptionist-facing UX safety acceptance criteria, copy boundaries, and live-provider blockers for R22 fake-provider scenario gates.

## My Understanding

We need to draft a receptionist-facing UX safety and scenario acceptance criteria review artifact. This document will define concrete rules for Bernie's structured outputs—focusing on ambiguity resolution, reason code compliance, availability deflection, and action-proposal copy boundaries—to ensure staff safety before live Gemini wiring.

## Intended Surface / Boundary

Orchestration review documentation under the orchestration/ directory. No production codebase files, UI components, or DB schemas will be modified.

## Out Of Scope

Live Gemini/Vertex AI integrations, production backend/frontend logic updates, database schema changes, and live network calls.

## Files I Expect To Edit

orchestration/fake_provider_scenario_ux_acceptance_review.md

## Implementation Steps

1. Analyze R22 fake-provider scenario gates, R21 safety reviews, and release rules. 2. Draft the new UX safety review artifact detailing the receptionist-facing copy boundaries, scenario expectations (ambiguity, reasons, collisions), and live readiness blockers. 3. Double-check references to STATUS_SPECIFIC_REASON_CODE_POLICY and capability_manifest.py. 4. Save the artifact and perform verification check.

## Visual / Behavioural Acceptance Checks

An orchestration review document is created containing: accepted/rejected scenario expectations, staff-facing copy boundaries (humble proposals), and live-provider readiness gates. The file must be fully self-contained and clear for Codex orchestration.

## Risks / Ambiguities

The primary risk is ensuring that the copy guidelines are realistic and matches the schemas in app/schemas/appointments.py. Since there is zero production code alteration, there are no runtime execution or regression risks.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
