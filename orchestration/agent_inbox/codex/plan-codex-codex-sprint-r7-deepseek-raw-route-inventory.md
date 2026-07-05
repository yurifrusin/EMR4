# plan-codex-codex-sprint-r7-deepseek-raw-route-inventory

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint-r7-raw-route-inventory` |
| Source Task | `codex-sprint-r7-deepseek-raw-route-inventory` |
| Status | integrated |
| Created | 2026-07-05 17:16 +1000 |
| Source HEAD | `e7e891f` |

## Plan Summary

Raw appointment temporal route inventory plan

## My Understanding

Inventory raw appointment mutation/proposal routes for past-date and fully elapsed same-day temporal bypasses; produce docs/receptionist_review_r7_route_inventory.md after approval. DeepSeek preliminary finding: raw compat and staff proposal mutation routes lack explicit temporal guards while Bernie tool-intent paths are partially guarded.

## Intended Surface / Boundary

docs/receptionist_review_r7_route_inventory.md only during implementation; static review of app/routers/appointments.py and adjacent tests.

## Out Of Scope

Production code, tests, migrations, UI/assets, live provider calls, broad security scan.

## Files I Expect To Edit

docs/receptionist_review_r7_route_inventory.md

## Implementation Steps

Map raw create/update/proposal routes; classify existing temporal guard state; name minimum route guards/tests; submit artifact.

## Visual / Behavioural Acceptance Checks

Artifact names exact surfaces, fail-open/fail-closed state, and R7 must-have tests.

## Risks / Ambiguities

Route aliases and compatibility helpers may share code; avoid duplicating Claude implementation lane.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
