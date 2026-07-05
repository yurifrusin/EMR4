# plan-antigravity-antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r23-frame-aware-fake-provider-ux-semantics` |
| Status | pending_plan_review |
| Created | 2026-07-05 23:00 +1000 |
| Source HEAD | `b425002` |

## Plan Summary

Define receptionist-safe frame-shape acceptance criteria and live readiness blockers for R23 fake-provider UX semantics.

## My Understanding

We must define frame-shape acceptance criteria for proposal, clarify, refusal, and read_request frames. We will identify which keys/values must or must-not appear for each frame type to preserve clinical safety before any live provider dry-run.

## Intended Surface / Boundary

Orchestration review documentation under the orchestration/ directory. No production codebase files, UI components, or DB schemas will be modified.

## Out Of Scope

Live Gemini/Vertex AI integrations, production backend/frontend logic updates, database schema changes, and live network calls.

## Files I Expect To Edit

orchestration/fake_provider_frame_shape_acceptance_criteria.md

## Implementation Steps

1. Analyze scenario gates in manifest_eval.py and R22 closeout. 2. Draft the frame-shape rules (must/must-not fields) for the 4 frame kinds (proposal, clarify, refusal, read_request). 3. Identify explicit blockers for live provider dry-run. 4. Save findings in orchestration/fake_provider_frame_shape_acceptance_criteria.md.

## Visual / Behavioural Acceptance Checks

A clear orchestration artifact is created under orchestration/ documenting the accepted/rejected frame shapes and live-provider readiness blockers. The artifact must be clear for Codex review.

## Risks / Ambiguities

Since this sprint involves documentation only, there are no runtime codebase or regression risks. The primary risk is ensuring alignment between heuristic copy restrictions and the backend capability manifest.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
