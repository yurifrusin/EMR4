# claude-sprint-r7-raw-temporal-guard-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | ad2ea75 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r7-raw-temporal-guard-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r7-raw-temporal-guard-contract --commit-message "Sprint R7 Raw Temporal Guard Contract" --message "claude-sprint-r7-raw-temporal-guard-contract ready for Codex review"` |

## Mission

Implement explicit temporal/date guardrails for raw appointment create/update and compatibility proposal paths, using existing diary temporal policy helpers where safe.

## Scope

### In Scope

app/routers/appointments.py; app/services/diary/temporal.py only if a tiny reusable helper is needed; focused backend tests for direct create/update/proposal temporal rejection or clarification semantics.

### Out of Scope

Diary UI, taskpane/Word assets, migrations, live provider calls, broad route rewrites, signed-confirm authority redesign, receptionist scenario corpus changes unless needed for a focused regression.

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

Run py_compile for touched backend/tests and focused pytest for raw appointment temporal guards plus adjacent existing appointment proposal/status tests selected by the implementation plan.

## Merge Criteria

Past absolute dates and fully elapsed same-day raw mutation windows cannot silently create or move appointments; compatible paths keep existing signed-confirm/evidence boundaries; tests prove no regression for valid future/same-day-open requests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - app/services/diary/temporal.py — added evaluate_raw_mutation_temporal_guard() pure helper + RawMutationTemporalKind Literal; updated __all__
  - app/routers/appointments.py — imported the helper; added temporal guard in _create_appointment_from_body (raises HTTP 422); added temporal guard in _apply_appointment_update (gated on date/time/duration keys, raises HTTP 422); added temporal block in _build_create_appointment_proposal (blocks list → safe=False, no signed evidence); added temporal block in propose_update_appointment (gated on date/time/duration incoming keys)
  - tests/test_appointment_raw_temporal_guard.py — new; 13 tests, all clock monkeypatching local per-test (no autouse fixture per Ariadne amendment)

- Verification run:
  - py_compile clean on all 3 files (python 3.14)
  - git diff --check: clean (no whitespace issues)
  - Pure-helper unit assertions (5 cases: past_date, window_fully_past, boundary, open-window, future) all passed without DB
  - Full integration test suite (pytest tests/test_appointment_raw_temporal_guard.py) could not run: no PostgreSQL running in claude/current worktree (port 5434 refused). Integration tests require a running DB. DB-level verification deferred to Codex integration environment.

- Remaining risks:
  1. Integration tests unverified locally (no DB in worktree). All 13 tests need Codex to run pytest against the integration DB.
  2. The create proposal builder now fires the temporal guard on every call (no "only when temporal fields in incoming" gate, because it is always a fresh create). This is correct but Codex should confirm the confirm_create_proposal route revalidates via _build_create_appointment_proposal, which will also re-gate — this is intentional and adds a defence-in-depth re-check at confirm time.
  3. Status/delete/waiting-area routes untouched per scope (they do not change appointment_date/start_time_local).
