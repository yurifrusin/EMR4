# plan-antigravity-antigravity-sprint-r3-stale-session-domain-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r3-stale-session-domain-review` |
| Status | pending_plan_review |
| Created | 2026-07-05 14:53 +1000 |
| Source HEAD | `f8bc6c8` |

## Plan Summary

Write R3 domain-acceptance review document and author new test fixtures for stale-session/revision coordinates.

## My Understanding

As the receptionist-domain reviewer (Gemini), we are tasked with writing the Sprint R3 Domain Acceptance review. The goal is to define acceptance cases and dissent for:
1. Stale browser tabs: Reload logic, blocking stale actions, and safe user copy.
2. Two receptionists (concurrency): Server-side check of session revision coordinates, rejecting conflicts with HTTP 409 (stale_session_revision).
3. Correction-vs-clarification: Merge logic overriding existing constraints if explicitly modified, but preserving others.
4. Intent switch: Discarding aborted booking/extension frame parameters entirely during pivot.
5. Safe failure behavior: Clinical safety (fail-closed) and professional, user-friendly copy.

We will draft the review artifact docs/receptionist_review_r3.md and create scenario fixtures tests/fixtures/bernie_scenarios/ to test these behaviors.

## Intended Surface / Boundary

docs/receptionist_review_r3.md and new YAML fixtures under tests/fixtures/bernie_scenarios/.

## Out Of Scope

Production backend session/revision implementation (Workstream R3-A), frontend UI/visual component changes, live model calls, database schema/migration changes.

## Files I Expect To Edit

docs/receptionist_review_r3.md, and new scenario files tests/fixtures/bernie_scenarios/stale_session_*.yaml.

## Implementation Steps

1. Draft docs/receptionist_review_r3.md covering stale browser tabs, two receptionists concurrency, correction-vs-clarification overrides, intent switches, and safe failure copy.
2. Write new scenario fixtures in tests/fixtures/bernie_scenarios/ mapping out the expected turn-by-turn domain states.
3. Validate fixtures with pytest tests/test_bernie_scenario_integrity.py.
4. Submit the plan and wait for 'complete sprint task' approval.

## Visual / Behavioural Acceptance Checks

Fixture integrity test passes successfully. The review document provides clear, actionable domain acceptance criteria for all 5 domains.

## Risks / Ambiguities

Ensure the backend stale-session HTTP error format (e.g., stale_session_revision code) aligns with what the client expects, and the scenario runner handles session_state_guard outcomes cleanly.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
