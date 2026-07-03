# codex-sprint-n9-diary-session-coordinate-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 0174ffe |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-n9-diary-session-coordinate-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-n9-diary-session-coordinate-invariants --commit-message "Sprint N9 Diary session coordinate invariants" --message "codex-sprint-n9-diary-session-coordinate-invariants ready for Codex review"` |

## Mission

Produce an invariant plan for the Diary-side bridge from N6 server sessions to N8 route outcome wiring.

## Scope

### In Scope

Plan first. docs/diary/diary.js and review/test_diary_smoke.py only; inspect backend N8 contract as needed. Prove active server session coordinates are sent, stale revisions block confirm, no browser PHI/session authority is introduced, and session_binding is carried unchanged.

### Out of Scope

No backend production code before plan approval. No persisted sessions, GraphRAG, taskpane, Command Centre, auto-mode, broad UI redesign, or new state-machine dependency.

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

Focused route-intercepted Playwright/pytest diary smoke checks; node --check; frontend version check; git diff --check.

## Merge Criteria

Plan gives exact DOM/API assertions for interpret payload, supervised payload, confirm payload, stale banner path, and no local/session storage PHI.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `docs/diary/diary.js`, `docs/diary/diary.html`, `review/test_diary_smoke.py`, `app/schemas/appointments.py`, `app/routers/appointments.py`, `tests/test_bernie_route_outcome_events.py`.
- Verification run: `node --check docs\diary\diary.js`; `python -m py_compile app\schemas\appointments.py app\routers\appointments.py`; `pytest tests\test_bernie_route_outcome_events.py -q`; focused and full `review/test_diary_smoke.py`; adjacent Bernie/session/evidence suites; frontend version check; `git diff --check`.
- Remaining risks: Browser now carries server coordinates and backend-stamped binding, but server sessions remain process-local and non-persistent until the later persistence sprint.
