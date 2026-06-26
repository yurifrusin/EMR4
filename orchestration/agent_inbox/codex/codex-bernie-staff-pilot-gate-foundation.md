# codex-bernie-staff-pilot-gate-foundation

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-staff-pilot-gate-foundation` |
| Status | submitted |
| Created | af5f897 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-staff-pilot-gate-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-staff-pilot-gate-foundation --commit-message "Dispatch Sprint 59 Bernie staff pilot gate" --message "Sprint 59 dispatched: Bernie staff pilot gate foundation"` |

## Mission

Create the narrow backend/config foundation for a staff-visible Bernie review pilot without enabling ordinary production exposure. The goal is a deterministic, centrally testable eligibility gate that later frontend work can consume before showing Bernie review outside explicit dev/query mode.

## Scope

### In Scope

Codex worker may inspect existing Bernie dev/review routes and settings, then propose a bounded backend/config design for a non-default pilot gate. Likely scope includes settings/env parsing, a small helper or route response field that reports whether the current authenticated staff/practice is eligible for Bernie pilot review, and focused tests proving default-off behavior, explicit opt-in behavior, auth/practice scoping, and no appointment writes/LLM/provider calls. Update orchestration docs only as needed for the sprint packet/review.

### Out of Scope

No frontend UI exposure, no production/default enablement, no autonomous Bernie writes, no PHI or real account allowlists, no Google/Gemini/provider calls, no appointment mutation semantics, no database migration unless the plan proves it is essential and low-risk, no broad refactor of appointment/Bernie route logic.

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

Plan must name exact files and tests. Implementation verification should include py_compile for touched backend modules, focused pytest for the pilot gate/default-off/allowlist behavior, adjacent Bernie dev/review payload tests if relevant, explicit no-write/no-audit/no-LLM proof, and git diff hygiene.

## Merge Criteria

Codex can integrate only if the pilot gate is default-off, deterministic, scoped to authenticated staff/practice or explicit non-PHI config, has compact tests, does not expose Bernie review broadly, and leaves existing dev/query-gated review behavior intact.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/config.py`; `app/services/bernie_pilot_gate.py`; `app/schemas/appointments.py`; `app/routers/appointments.py`; `tests/test_bernie_staff_pilot_gate.py`; `orchestration/agent_inbox/codex/codex-bernie-staff-pilot-gate-foundation.md`
- Verification run: `python -m py_compile app\config.py app\services\bernie_pilot_gate.py app\routers\appointments.py app\schemas\appointments.py` passed; `python -m pytest ...` could not run under system Python because pytest is not installed; `.venv\Scripts\python.exe -m py_compile app\config.py app\services\bernie_pilot_gate.py app\routers\appointments.py app\schemas\appointments.py` passed; `.venv\Scripts\python.exe -m pytest tests\test_bernie_staff_pilot_gate.py tests\test_bernie_dev_fixtures.py tests\test_bernie_supervised_booking_wrapper.py -q` passed with 31 tests; `git diff --check` passed. Focused tests cover default-off, enabled-without-allowlist fail-closed, practice/user allowlist scoping, malformed allowlist fail-closed, auth requirement, no appointment/audit writes, and no provider/LLM/mutation calls in the new route/service source.
- Remaining risks: The gate is intentionally standalone and backend-only; later frontend work still needs to consume `/api/v1/appointments/bernie/pilot-eligibility` before showing Bernie review outside explicit dev/query paths. No frontend exposure, appointment mutation, audit write, provider call, or migration was added.
