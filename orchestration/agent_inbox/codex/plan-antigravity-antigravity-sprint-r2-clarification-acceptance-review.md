# plan-antigravity-antigravity-sprint-r2-clarification-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r2-clarification-acceptance-review` |
| Status | pending_plan_review |
| Created | 2026-07-05 14:08 +1000 |
| Source HEAD | `89cb837` |

## Plan Summary

Receptionist-domain acceptance criteria, fixture critique, and dissent for clarification merge semantics

## My Understanding

Sprint R2 introduces selective clarification merge semantics on the backend to prevent overwriting resolved request-frame fields (patient, practitioner, date, time) when resolving missing fields. My role is to provide independent domain and test-design review, critiquing existing fixtures, designing additional test scenarios, and verifying that the implementation meets receptionist workflow invariants without regression or stale state resurrecting.

## Intended Surface / Boundary

YAML scenario fixtures under tests/fixtures/bernie_scenarios/ and a receptionist-domain review report under docs/receptionist_review_r2.md. No UI or production code files are affected.

## Out Of Scope

Production backend implementation (Claude Code), Diary frontend visual changes or code, live provider prompt engineering, GraphRAG vector DB wiring, and direct master/handoff updates.

## Files I Expect To Edit

tests/fixtures/bernie_scenarios/*.yaml, docs/receptionist_review_r2.md

## Implementation Steps

1. Analyze existing R1 clarification scenarios for domain coverage. 2. Design and add new scenarios to tests/fixtures/bernie_scenarios/ covering multi-turn clarifications, correction vs clarification distinction, and stale session guards. 3. Validate scenario parsing using fixture integrity tests. 4. Author a receptionist-domain review report detailing checklist and dissent.

## Visual / Behavioural Acceptance Checks

All scenario replay tests pass (including un-xfailing Sprint R2 merge tests); new scenario fixtures parse successfully under integrity checks; review report captures all edge cases (merge fields, correction intents, session resurrection, extension vs booking).

## Risks / Ambiguities

Selective merge logic must correctly distinguish clarification of a missing field from a user correcting an already-resolved field. Stale session values must not be accidentally resurrected during a merge.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
