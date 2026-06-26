# plan-claude-claude-noshow-dna-status-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-noshow-dna-status-contract` |
| Status | integrated |
| Created | 2026-06-26 16:22 +1000 |
| Source HEAD | `909df00` |

## Plan Summary

Prove and, only if a gap surfaces, harden the backend appointment status-proposal contract so NoShow and DNA attendance outcomes are terminal, non-blocking, practice-scoped, and never mutate state before explicit confirmation. The semantics already exist in code (both statuses are in TERMINAL_STATUSES and NON_BLOCKING_STATUSES); the work is mainly focused pytest coverage that pins the NoShow/DNA branch explicitly, plus narrow code hardening only if a test exposes a real contract gap.

## My Understanding

NoShow and DNA are attendance outcomes that must behave like terminal, non-blocking statuses. In app/routers/appointments.py they are already members of TERMINAL_STATUSES (so propose_status_update returns autonomy_tier='proposal', safe=True, requires_confirmation=True for them, and warns 'already_terminal' when re-transitioning a terminal appointment) and NON_BLOCKING_STATUSES (so _find_conflicting_appointment and get_available_slots skip them, freeing the slot). _get_appointment enforces practice scoping (cross-practice -> 404). The proposal endpoints are non-mutating; PATCH /{id}/status is the only confirmed write and clears waiting_area_id on terminal transitions. Existing tests cover NoShow/DNA for PATCH acceptance, waiting-room disappearance, and conflict slot-freeing, but the proposals/status terminal branch is currently proven only via Completed/Cancelled. This task pins NoShow/DNA explicitly through the proposal contract and proves no premature mutation.

## Intended Surface / Boundary

Backend only: app/routers/appointments.py status-proposal and status-mutation contract for NoShow/DNA, plus focused pytest files under tests/. The contract surface is JSON proposal/command payloads and DB state, not any rendered UI.

## Out Of Scope

No diary frontend, taskpane, or Command Centre changes. No diary grid cards/slots/stacking/panels/waiting-room visual changes. No cancellation reason/note capture, no cancelled-appointment review UI, no recurrence, no SMS/reminders, no billing, no broad audit logging. No new migration unless a verified backend contract gap genuinely requires a schema change (not anticipated). app/schemas/appointments.py only if a test exposes a real shape gap.

## Files I Expect To Edit

tests/test_appointment_status_mutations.py (extend) and/or tests/test_appointment_update_proposal.py (extend) for NoShow/DNA proposal and mutation coverage; possibly a small new tests/test_noshow_dna_status_contract.py if cleaner. app/routers/appointments.py ONLY if a test exposes a real gap (not expected). app/schemas/appointments.py only if a real shape gap surfaces.

## Implementation Steps

1) Re-read the NoShow/DNA paths in app/routers/appointments.py (TERMINAL_STATUSES, NON_BLOCKING_STATUSES, propose_status_update, update_appointment_status, _find_conflicting_appointment, get_available_slots). 2) Add focused tests proving, for BOTH NoShow and DNA: (a) POST proposals/status to the outcome returns safe=True, requires_confirmation=True, autonomy_tier='proposal' (terminal branch), command.status echoes the outcome, and the DB row is unchanged after the proposal; (b) proposing the same outcome the appt already has -> blocked 'already_in_status'; (c) re-transitioning away from an existing NoShow/DNA -> 'already_terminal' warning, tier='proposal', row unchanged; (d) transitioning to NoShow/DNA from an appt in a waiting area -> clears_waiting_area True + 'waiting_area_cleared' warning, row unchanged. 3) Add/confirm tests proving non-blocking semantics for NoShow/DNA via GET /slots (a NoShow/DNA appt leaves its slot 'available'), complementing the existing create-conflict slot-freeing test. 4) Add a practice-scoped test: POST proposals/status for another practice's appt -> 404. 5) Confirm PATCH /{id}/status to NoShow/DNA clears waiting_area_id (terminal write path). 6) Only if a test reveals a real contract gap, apply minimal hardening in appointments.py (and schemas if strictly needed) to close it; otherwise leave production code unchanged and rely on the proofs. 7) Run verification.

## Visual / Behavioural Acceptance Checks

Behavioural/contract checks (no UI): proposals/status for NoShow and DNA is non-mutating (DB row identical after call) and returns the terminal proposal contract (safe, requires_confirmation, tier='proposal'); same-status -> blocked; re-transition from terminal -> already_terminal warning; to-terminal-from-area -> clears_waiting_area + warning; NoShow/DNA do not block conflicts and leave /slots available; cross-practice proposal -> 404; PATCH to NoShow/DNA clears waiting_area_id. No diary/taskpane/Command Centre surface changes.

## Risks / Ambiguities

Main risk: scope creep into UI or cancellation-reason work -- explicitly out of scope. The contract appears already correct, so the likely outcome is added tests with no production code change; that is acceptable per merge criteria (semantics proven unchanged). If a gap surfaces, hardening must stay inside appointments.py/schemas and avoid behavioural changes to Completed/Cancelled paths. Ambiguity: dedicated new test file vs extending existing ones -- I will extend existing files unless that bloats them, to keep the diff reviewable. No migration expected; will flag immediately if one becomes necessary rather than introducing schema churn.

## Codex Plan Review

- Review result:
- Required changes before implementation: none; approved by Ariadne after review of the plan and current backend contract.
- Approved to proceed: yes; implementation subsequently integrated as a focused test-only proof suite.
