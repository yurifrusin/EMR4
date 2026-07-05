# Plan: codex-sprint-r5-deepseek-executable-scenario-promotion

## Summary

Promote selected R3/R4 natural-language Bernie receptionist corpus fixtures into executable scenario replay coverage. Start with past-date guardrails (absolute past date blocking, same-day past-window clarification) where the existing harness action set (normalize/search/select/confirm) or a minimal supervised-booking wrapper action can express the behavior cleanly.

## Understanding

The codebase has two fixture kinds in tests/fixtures/bernie_scenarios/:

1. **NL corpus fixtures** (17 files): natural-language turns with `user` text + `expect.outcome`/`expect.reason_codes`. These are *specifications*; the loader skips them via NonExecutableScenario.

2. **Executable replay fixtures** (2 harness_demo_*.yaml files): structured turns with `action` (normalize/search/select/confirm), `input`, and `expect.fields`. These run against real backend API endpoints via replay.py with a forbidden-AI-provider guard.

The replay harness actions map to:
- `normalize` ? POST /api/v1/appointments/proposals/slot-search/normalize
- `search` ? POST /api/v1/appointments/proposals/slot-search/normalized
- `select` ? POST /api/v1/appointments/proposals/slot-search/selection
- `confirm` ? POST /api/v1/appointments/proposals/create/confirm-bernie

Currently no `action: interpret` or `action: supervised-booking` exists, so NL scenarios testing the interpret route or supervised-booking wrapper cannot be promoted as-is.

## Surface/Boundary

**In scope (promotable):**
- tests/fixtures/bernie_scenarios/absolute_past_date_blocked.yaml
- tests/fixtures/bernie_scenarios/booking_no_matching_times_only_after_slot_search_empty.yaml
- tests/fixtures/bernie_scenarios/booking_roster_unavailable_distinct_from_no_slots.yaml
- tests/fixtures/bernie_scenarios/same_day_past_window_clarify.yaml (assess feasibility)

**Out of scope (not yet promotable):**
- Stale-session/revision fixtures (concurrency conflict, reload blocking, correction/pivot): require session-freshness setup that the replay harness does not provide
- Clarification-merge fixtures (preserves patient/date/practitioner during clarification): require NL interpret flow
- Booking-to-extension switch: requires intent pivot not in action set
- Extension-duration fixtures: require appointment-extension endpoints not in action set
- Tomorrow-not-blocked advisory: requires seeded appointments + advisory checking

## Files to create

1. tests/fixtures/bernie_scenarios/exec_absolute_past_date_blocked.yaml
   Executable fixture: normalize with past date_from -> safe=false, blocks contain requested_date_in_past, forbidden appointment_written/audit_written.

2. tests/fixtures/bernie_scenarios/exec_no_matching_times_empty_slots.yaml
   Executable fixture: normalize + search with empty roster slots -> search response candidates=[], safe=true (no slot found is safe, not blocked).

3. tests/fixtures/bernie_scenarios/exec_roster_unavailable.yaml
   Executable fixture: supervised-booking-style normalize with no roster -> blocked before slot search.

4. tests/fixtures/bernie_scenarios/exec_same_day_past_window.yaml (if feasible — see risks)

## Steps

1. Inspect slot-search normalize endpoint response schema for blocked responses (blocks array, constraint=null, safe=false). Confirm the NL fixture `absolute_past_date_blocked.yaml` maps exactly to a normalize action with past `date_from`.

2. Inspect slot-search endpoint response schema for the empty-slot-search case. Confirm that the search endpoint returns candidates=[], safe=true when roster exists but has zero matching slots.

3. Inspect supervised-booking wrapper endpoint response schema for roster-unavailable scenario. Determine if a new `action: supervised-booking` should be added to the replay harness, or if the existing `action: normalize` + field assertion on the response can detect roster unavailability.

4. Assess the same-day past-window fixture: determine whether the normalize endpoint or a supervised-booking action can express a same-day time window that has already passed (simulated_clinic_time injection). If not, add a `HARNESS_GAP` note and skip for this sprint.

5. Create executable fixture `exec_absolute_past_date_blocked.yaml` with:
   - reference_date aligned to the normalized command's constraint check
   - action: normalize with past date_from
   - expect.status=200, expect.fields.safe=false, expect.fields."blocks[0].code"="requested_date_in_past"
   - forbidden_outcomes: [provider_called, appointment_written, audit_written]

6. Create executable fixture `exec_no_matching_times_empty_slots.yaml` (if step 2 confirms clean mapping) with:
   - reference_date and initial_state defining roster with empty slots
   - action: normalize then action: search
   - Assert candidates empty, no blocking codes
   - Use xfail if the search endpoint returns 500/error for empty-roster case

7. Add `action: supervised-booking` support to replay.py if needed for step 3, OR document why the fixture stays NL-only.

8. Run integrity checks on all new fixtures.

## Acceptance Criteria

- [ ] `exec_absolute_past_date_blocked.yaml` passes: normalize with past date_from returns safe=false with requested_date_in_past block code, no appointment/audit rows written
- [ ] `exec_no_matching_times_empty_slots.yaml` passes: normalize succeeds, search returns empty candidate list, no forbidden outcomes fire
- [ ] `exec_roster_unavailable.yaml` (or documented NL-only): roster_unavailable is correctly distinguished from no_matching_times
- [ ] All new fixtures pass the existing integrity validator (test_bernie_scenario_integrity.py)
- [ ] All new fixtures run through the parametrized replay harness (test_bernie_scenario_replay.py)
- [ ] `same_day_past_window_clarify.yaml` is either promoted or has a documented HARNESS_GAP note explaining why it cannot be expressed with current actions
- [ ] No production code changes: only new YAML fixture files and potentially replay.py action dispatch

## Risks

1. **No supervised-booking action**: The replay harness has no `action: supervised-booking`. Adding it requires modifying replay.py (the harness code, not production code). If this is out of policy, these fixtures stay NL-only.

2. **Empty-slot search response**: The search endpoint may return 200 with success=true but candidates=[] for an empty roster, or it may return a different status. If the response schema is ambiguous, the fixture will need xfail.

3. **Same-day past-window needs clinic-time injection**: The NL fixture uses `simulated_clinic_time` which doesn't exist in the current harness initial_state. Without a way to inject clinic-local-now, this path cannot be tested through the replay engine.

4. **Slot selection without schedule fixture**: The conftest schedule fixture may not provide the right roster/slot data for empty-roster cases. May need to add initial_state roster configuration to the fixture loader.

