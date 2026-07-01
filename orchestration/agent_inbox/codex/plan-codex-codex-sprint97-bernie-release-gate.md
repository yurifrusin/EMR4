# plan-codex-codex-sprint97-bernie-release-gate

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint97-bernie-release-gate` |
| Source Task | `codex-sprint97-bernie-release-gate` |
| Status | integrated |
| Created | 2026-07-01 09:50 +1000 |
| Source HEAD | `028e2a0` |

## Plan Summary

Repair Bernie release gates so ordinary prompt, true-live labeling, and screenshot failure are blocking.

## My Understanding

Sprint 96 passed deterministic route-intercepted and backend contract checks, but the simplest receptionist prompt for Margaret Thompson with Dr Shera was left as residual user review. Sprint 97 should make that ordinary prompt a hard release gate, distinguish smoke/fixture and mocked-live checks from true provider-backed live checks, and prevent closeout while the reported screenshot failure remains reproducible.

## Intended Surface / Boundary

Review and orchestration surfaces only: Bernie review harness naming/markers, Bernie interpreter smoke tooling, closeout/protocol release-gate wording. Affected visible surface is the diary Bernie staff review flow only as a tested behavior; nearby diary grid, booking slot cards, waiting room/status panels, taskpane, Command Centre, and production API behavior must not change during this planning task.

## Out Of Scope

No production backend/frontend implementation before approval; no app/, docs/diary runtime, migrations, provider credentials, GCP console work, phone/Medicare/OPV/PVM integration, broad orchestration rewrite, or weakening confirmation/audit/RBAC gates.

## Files I Expect To Edit

Expected after approval: review/test_diary_smoke.py; scripts/smoke_bernie_interpreter.py; tests/test_smoke_bernie_interpreter_script.py; possibly tests/test_bernie_interpret_booking_instruction.py for ordinary-prompt contract naming only; orchestration/sprint_closeout.md; orchestration/protocol_alerts.md or a small release-gate checklist under orchestration/ if Ariadne prefers not to overload alerts. Plan packet only changed now.

## Implementation Steps

1. Rename or mark route-intercepted diary tests so no test containing page.route API interception is described as live; use names like route_intercepted, smoke_fixture, or mocked_provider. 2. Add a deterministic automated gate for the ordinary Margaret Thompson/Dr Shera prompt using fake provider or mocked live provider, asserting interpreted result, resolved practitioner/patient, no appointment/audit write, no raw UUID/snake_case in staff-facing evidence where applicable. 3. Extend smoke_bernie_interpreter.py with an explicit ordinary-prompt preset or --ordinary-bernie-gate option using non-PHI dev fixtures, and require provider_metadata/live_provider truth in output; keep --allow-live mandatory for gemini_vertex. 4. Add a true-live readiness gate that either runs with --provider gemini_vertex --allow-live and asserts live_provider true plus expected ordinary-prompt outcome, or exits/skips as a blocking xfail/fail policy when live credentials are absent for a release candidate. 5. Add closeout/protocol wording that basic happy-path Bernie booking review cannot be listed as optional residual user review; if the ordinary prompt or screenshot reproduction fails, Sprint 97 closeout status remains blocked. 6. Re-run focused pytest/smoke commands and git diff checks only after implementation approval.

## Visual / Behavioural Acceptance Checks

Hard gates: ordinary prompt 'Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45' has a deterministic automated pass condition; route-intercepted Playwright tests are named/reported as route-intercepted and never as live; true provider-backed checks require live_provider true or produce a blocking skip/fail release note; closeout text treats unresolved screenshot reproduction as blocking; confirmation remains explicit and non-mutating tests still prove no write before Confirm booking.

## Risks / Ambiguities

Main ambiguity is whether Ariadne wants live-provider absence to fail local CI or be a release-candidate-only gate; my recommendation is normal CI runs fake/route-intercepted gates, while release closeout requires either a passing true-live smoke or an explicit blocked closeout. Screenshot failure details may live outside repo; implementation should encode the reproducible assertion once Ariadne supplies the exact failing state/screenshot symptom.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
