# plan-claude-claude-claude-bernie-slot-search-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-claude-bernie-slot-search-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-26 20:49 +1000 |
| Source HEAD | `e1ec8a4` |

## Plan Summary

Add a non-mutating POST /api/v1/appointments/proposals/slot-search endpoint: typed constraint object in, ranked candidate slots plus warnings/blocks/summary out. Read-only precursor to POST /proposals/create. Writes no appointments and no audit rows. No LLM, no Bernie runtime, no UI.

## My Understanding

Bernie pipeline: LLM parses NL into a typed constraint object, then deterministic find_slots (no LLM) runs against real roster/schedule/conflict/break data, then present/confirm/write. This sprint builds ONLY the deterministic search stage backend contract as a non-mutating proposal endpoint. It is the read-only precursor to the existing POST /proposals/create; picking a candidate later flows into that separate create proposal. No LLM, no Bernie runtime, no UI.

## Intended Surface / Boundary

Backend appointment/slots/proposal only. New typed schemas in app/schemas/appointments.py; one new route POST /appointments/proposals/slot-search in app/routers/appointments.py mirroring existing proposal endpoints (safe/requires_confirmation/autonomy_tier/summary/warnings/blocks). Reuses _practice_zoneinfo, _find_conflicting_appointment, _get_break_overlaps, _local_datetime, schedule/override resolution, MUTATING_APPOINTMENT_ROLES, NON_BLOCKING_STATUSES. Practice-scoped (practitioner must belong to current_user.practice_id else 404), role-gated to MUTATING_APPOINTMENT_ROLES, location-aware via existing location_id conflict filter. Slots/candidates here are JSON data, not a visual surface; no diary grid, waiting room, booking modal, taskpane, or Command Centre code is touched.

## Out Of Scope

Diary UI, autonomous Bernie runtime, LLM/Gemini calls, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, ANY appointment or audit-row mutation, and broad scheduling redesign.

## Files I Expect To Edit

app/schemas/appointments.py (new SlotSearchProposalIn, SlotCandidate, SlotSearchProposalOut); app/routers/appointments.py (new route + small behaviour-preserving _resolve_day_schedule helper extracted from get_available_slots); tests/test_slot_search_proposal.py (new focused tests).

## Implementation Steps

1. Schemas. SlotSearchProposalIn constraint object: practitioner_id (required), date_from (required), date_to (optional, default date_from, range capped ~14 days), duration_minutes (optional gt=0 le=480), appointment_type_id (optional, derives duration when duration omitted), location_id (optional), earliest_time/latest_time (optional within-day window), patient_id (optional), limit (default 20, cap 100). SlotCandidate: appointment_date, start_time (tz-aware), end_time, start_time_local, duration_minutes, per-candidate warnings. SlotSearchProposalOut: intent=search_slots, safe, requires_confirmation=False, autonomy_tier (execute_with_report|blocked), summary, resolved_duration_minutes, candidates, warnings, blocks.
2. Extract _resolve_day_schedule(db, practitioner_id, target_date) -> (start_t,end_t,slot_mins)|None from get_available_slots and reuse it there unchanged (proven by tests/test_slots.py).
3. Route: role-gate to MUTATING_APPOINTMENT_ROLES; verify practitioner in practice (404). Resolve duration (explicit else appointment-type default); if none -> blocks missing_duration, autonomy_tier=blocked, empty candidates. If date_to<date_from or range too large -> blocks invalid_range. For each day in window resolve schedule, generate candidate starts on the schedule slot grid, keep a candidate only if full requested duration fits before day end and _find_conflicting_appointment(location_id=...) is empty; attach break_overlap warnings via _get_break_overlaps; respect earliest_time/latest_time. Rank earliest-first across days, cap at limit. Build human summary. No db.add/db.commit.
4. Tests as in acceptance.

## Visual / Behavioural Acceptance Checks

JSON API; no rendered surface changes (diary grid, waiting room, booking slot cards, status colours, taskpane, Command Centre all unchanged). tests/test_slot_search_proposal.py proves: 401 unauthenticated; 404 cross-practice practitioner; candidates earliest-first with correct requested duration and tz-aware times; a blocking appointment removes overlapping candidates while Cancelled/NoShow/DNA do not; break overlap surfaces a per-candidate warning yet still offers the candidate; missing duration + no appointment type -> autonomy_tier=blocked, empty candidates; invalid/oversized date range -> blocked; location filtering ignores conflicts in another location; a day with no schedule yields no candidates for that day; NON-MUTATING proof: appointment row count and audit-log row count identical before/after.

## Risks / Ambiguities

Extracting _resolve_day_schedule lightly touches get_available_slots; behaviour-preserving and covered by tests/test_slots.py (alternative is logic duplication, which I avoid). Candidate cadence uses the practitioner schedule slot grid (not arbitrary 5-min) to match current diary semantics; flagged if finer cadence wanted. Autonomy tier: read-only search uses execute_with_report with requires_confirmation=False since booking still needs the separate create proposal; trivial to switch to proposal if Codex prefers. Multi-day range is capped to bound query cost.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
