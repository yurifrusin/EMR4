# claude-waiting-area-resource-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | faf779b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-waiting-area-resource-contract --commit-message "Add waiting area resource contract" --message "Waiting area resource contract ready for Codex review"` |

## Mission

Add the backend contract needed to model named physical waiting areas and connect them to rooms/resources without collapsing waiting area, attendance status, and practitioner/resource identity into one concept. Keep this as the minimal Phase 2 foundation Bernie and the diary UI can safely consume later.

## Scope

### In Scope

app/models/tenancy.py, app/models/diary.py, app/schemas/diary.py, app/schemas/appointments.py, app/routers/diary.py, app/routers/appointments.py, Alembic migration if needed, seed.py, focused waiting-room/diary roster/template tests. Recommended shape: expose room/default waiting area metadata and allow GET /appointments/waiting-room to filter/group by waiting_room while preserving existing behaviour when no filter is supplied.

### Out of Scope

docs/diary frontend, taskpane/Command Centre, Bernie copilot implementation, patient-edit UI, drag/drop/resize, SMS reminders, billing/completion workflow, ADHA/IHI live integration.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run focused pytest for waiting-room, diary roster/template, appointment status/booking patient-flow if touched; run alembic upgrade/current if a migration is added; run py_compile on touched backend modules and git diff --check.

## Merge Criteria

Named physical waiting-area metadata is available to clients in a practice-scoped way; waiting-room endpoint remains backward compatible and can filter/group by waiting area; existing status/attendance semantics are not conflated with physical waiting area assignment; tests cover practice scoping and fallback/no-waiting-area behaviour.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
