# claude-claude-bernie-slot-search-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 3645361 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-claude-bernie-slot-search-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-claude-bernie-slot-search-proposal-contract --commit-message "Claude Bernie Slot Search Proposal Contract" --message "claude-claude-bernie-slot-search-proposal-contract ready for Codex review"` |

## Mission

Plan first, then after approval add a non-mutating backend slot-search proposal contract for future Bernie/reception use so staff can ask for candidate appointment slots without creating or changing appointments.

## Scope

### In Scope

Plan packet first. After approval, backend appointment/slots/proposal surfaces only as needed, likely app/schemas/appointments.py, app/routers/appointments.py, and focused tests. The endpoint should be practice-scoped, auth/role-gated, location-aware where current slot logic supports it, return typed candidate slots plus warnings/blocks/summary, and must not write appointments or audit rows.

### Out of Scope

Diary UI implementation, autonomous Bernie runtime, LLM calls, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, mutation of appointments, and broad scheduling redesign.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan packet first. After approval: py_compile touched backend modules/tests; focused pytest proving role/practice scoping, no appointment/audit writes, expected candidate slot output, conflict/break/location handling where applicable, and git diff --check.

## Merge Criteria

Codex can verify a typed, non-mutating slot-search proposal endpoint suitable for future Bernie command previews, with tests passing and no production UI or appointment mutation changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/schemas/appointments.py — added SlotSearchProposalIn (practitioner_id, date_from, optional date_to capped 14 days, duration_minutes, appointment_type_id, location_id, earliest_time, latest_time, patient_id, limit), SlotCandidate (appointment_date, start_time UTC-aware, end_time, start_time_local, duration_minutes, per-candidate warnings), SlotSearchProposalOut (intent=search_slots, safe, requires_confirmation=False, autonomy_tier, summary, resolved_duration_minutes, candidates, warnings, blocks)
  - EDIT app/routers/appointments.py — extracted _resolve_day_schedule(db, practitioner_id, target_date) helper from get_available_slots (behaviour-preserving refactor, get_available_slots reuses it unchanged); added POST /proposals/slot-search route role-gated to MUTATING_APPOINTMENT_ROLES; no db.add/db.commit anywhere in the new route; reuses _find_conflicting_appointment, _get_break_overlaps, _utc_from_local, _practice_zoneinfo, and all _ensure_* guards
  - NEW tests/test_slot_search_proposal.py — 20 tests: 401 unauthenticated, 404 cross-practice, candidates earliest-first with correct duration and tz-aware times, limit cap, booked appt removes candidates, 30-min booking removes two slots, Cancelled/NoShow/DNA do not block, break overlap warns but candidate still offered, missing duration blocked, type default duration derived, date_to before date_from 422, range > 14 days 422, earliest_time/latest_time window, no-schedule day yields no candidates, conflict at other location does not block, non-mutating proof (row counts identical before/after)
- Verification run:
  - py_compile on all 3 touched/new Python files: OK
  - pytest tests/test_slot_search_proposal.py -v: 20 passed in 35.40s
  - pytest tests/ -q (full suite, 430+ tests): 0 failed, exit code 0
  - git diff --check: clean
- Remaining risks:
  - _resolve_day_schedule is a drop-in refactor of inline code from get_available_slots; behaviour unchanged and covered by test_slots.py (all passing).
  - Candidate cadence uses practitioner schedule slot grid, consistent with current diary semantics. Finer cadence configurable later by adjusting slot_mins.
  - autonomy_tier=execute_with_report / requires_confirmation=False is intentional: read-only search; booking still requires POST /proposals/create + confirmation.
