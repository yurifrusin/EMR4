
# plan-codex-codex-sprint-r7-deepseek-temporal-regression-tests

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | $branch |
| Source Task | codex-sprint-r7-deepseek-temporal-regression-tests |
| Status | pending_plan_review |
| Created | 2026-07-05 17:07 +10:00 |
| Source HEAD | $head |

## Plan Summary

Focused pytest regression tests for raw appointment temporal guardrails: absolute-past create/update rejection, same-day fully-elapsed window rejection, and future-date pass-through. Tests marked xfail before Claude's production guard implementation, then expected to pass after integration.

## My Understanding

The raw POST /api/v1/appointments (create_appointment) and PUT /api/v1/appointments/{id} (update_appointment) routes in app/routers/appointments.py currently have NO past-date temporal guard. They check only time conflicts via _raise_if_conflict. The AppointmentCreate schema validates field co-presence but does not reject absolute-past appointment_date values. Claude's parallel lane (claude-sprint-r7-raw-temporal-guard-contract) will add temporal guards to these routes.

My task: write focused regression tests (tests/test_appointment_raw_temporal_guards.py) that:
- Encode the expected past-date rejection behaviour (absolute past dates → 422/409 temporal guard response)
- Encode same-day fully-elapsed window behaviour (today + time already passed → temporal guard)
- Cover both direct create/update and compatibility proposal paths
- Use pytest.mark.xfail where the guard is not yet implemented
- Use straightforward conftest fixtures (client, db, gp_user, practice, practitioner, patient, appt_type)
- Do NOT touch production code, Claude's guard implementation files
- Do NOT touch diary UI, taskpane, migrations

Test scenarios are informed by the R6 edge-scout artifact (docs/receptionist_review_r6_edge_cases.md) and the R6 domain review (docs/receptionist_review_r6.md), which identified raw mutation date-policy as a deferred category now being addressed.

## Intended Surface / Boundary

Affected surface: Raw appointment CRUD temporal guard behaviour — tests/test_appointment_raw_temporal_guards.py (new file).

Nearby surfaces that must NOT change:
- Bernie interpret/supervised routes (have separate temporal guards)
- Diary UI grid / Waiting Room panels / booking slot UI
- Taskpane assets, Word documents, GitHub Pages
- Migration files, seed data
- Existing tests/test_appointment_raw_compat.py (raw compat evidence tests — keep separate)
- Existing tests/test_appointment_proposals.py, test_appointment_update_proposal.py (proposal contract tests)
- app/schemas/* (no schema changes unless fixture helpers touch it)
- Claude's production guard files (app/routers/appointments.py, app/services/diary/temporal.py)

Visually loaded words: appointment creation, appointment update, raw endpoint, temporal guard, past date rejection. This is backend-only route behaviour — no cards, slots, stacking, panels, waiting room, diary grid, or booking slot surfaces are changed.

## Out Of Scope

- Production code edits (app/ directory)
- Claude's temporal guard implementation (app/routers/appointments.py, app/services/diary/temporal.py)
- Diary UI / taskpane / Word assets
- Migration files
- Live provider calls / Gemini / Vertex AI
- Broad flaky suite expansion
- Bernie scenario corpus changes
- Raw route inventory review artifact (separate codex-sprint-r7-deepseek-raw-route-inventory packet)

## Files I Expect To Edit

- tests/test_appointment_raw_temporal_guards.py (new file)
- orchestration/agent_inbox/codex/codex-sprint-r7-deepseek-temporal-regression-tests.md (task status update)

## Implementation Steps

1. Create tests/test_appointment_raw_temporal_guards.py with:
   a. Import lines: uuid, datetime.date, datetime.time, datetime.timedelta, pytest
   b. Conftest fixtures: client, db, gp_user, practice, practitioner, patient, appt_type
   c. Helper: _make_appt similar to test_appointment_raw_compat.py pattern
   d. Helper: _future_create_body (returns appointment_date set to a future date — currently passes)
   e. Helper: _past_create_body (appointment_date a week ago — currently passes but SHOULD fail)

2. Test groups:
   a. TestFutureDateGroup: tests with a future appointment_date that should always pass
      - test_create_future_date_succeeds (201)
      - test_update_future_date_succeeds (200)
   b. TestAbsolutePastDateGroup: xfail tests expecting temporal guard
      - test_create_absolute_past_date_rejected (currently 201, xfail → expected 422/409 after Claude)
      - test_update_to_absolute_past_date_rejected (currently 200, xfail → expected rejection)
      - test_create_proposal_absolute_past_date_rejected (proposal path guard)
      - test_confirm_create_absolute_past_date_rejected (confirm path guard)
   c. TestSameDayFullyElapsedGroup: xfail tests for same-day fully-past time windows
      - test_create_today_fully_elapsed_time_rejected (today + time already passed)
      - test_update_today_fully_elapsed_time_rejected
   d. TestTodayFutureTimeGroup: today + future time should always pass
      - test_create_today_future_time_succeeds

3. Update task status field in source packet from "queued" to "pending_plan_review"
4. (After plan approval) Implement the tests with appropriate xfail markers
5. (After plan approval) Run py_compile verification
6. (After plan approval) Submit with the packet's submit command

## Visual / Behavioural Acceptance Checks

Verification after implementation:
- py_compile tests/test_appointment_raw_temporal_guards.py (clean syntax)
- pytest tests/test_appointment_raw_temporal_guards.py -q --tb=short (xfail tests show expected failures; non-xfail tests pass)
- pytest tests/test_appointment_raw_compat.py -q --tb=short (existing raw compat tests still pass)
- git diff --stat shows only new test file + task status update
- git diff --check shows no whitespace errors

After Claude's guard implementation is integrated:
- pytest tests/test_appointment_raw_temporal_guards.py -q (xfail tests now pass, prompting removal of xfail decorators)
- All regression tests remain green

## Risks / Ambiguities

- If Claude's guard implementation returns a different HTTP status code (e.g., 422 vs 409), the xfail expected code may need adjustment. Mitigation: use broad xfail such as @pytest.mark.xfail(strict=True, reason="Raw temporal guard not yet implemented — will pass after Claude integrates") and assert esp.status_code >= 400.
- If Claude's guard behaviour differs from the expected semantics (e.g., blocks only create but not update), test assertions will catch it.
- If the raw proposal paths (/proposals/create, /proposals/update) are restructured by Claude, proposal tests may need a narrower assertion scope.
- Clock-dependent tests (same-day fully elapsed) use hardcoded future/past offsets; CI run at midnight-adjacent times should still be deterministic because offsets are large (e.g., ±6 hours).
- Diary template fixtures may need location_id for Claude's guard; if so, the helper should include location_id=None default.
- This file must not import or depend on Claude's new production symbols (temporal helpers not yet in scope).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

