# claude-nurse-practitioner-dev-data-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | a095401 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-nurse-practitioner-dev-data-contract --commit-message "Nurse practitioner dev-data contract" --message "claude-nurse-practitioner-dev-data-contract ready for Codex review"` |

## Mission

Make Room 2/Nurse deliberately bookable by representing Nurse as a real practitioner/staff resource in dev data and tests, while preserving the current appointment contract that requires practitioner_id.

## Scope

### In Scope

seed.py; focused diary roster/template tests; focused appointment create/edit/slots tests only as needed; minimal backend fixes if existing code cannot represent a nurse practitioner/staff resource safely.

### Out of Scope

docs/diary frontend; taskpane/Command Centre; patient identity/duplicate work; waiting-area UI; room/resource-only bookings without practitioner_id; drag/drop/resize; broad schema redesign.

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

.venv\\Scripts\\python.exe -m pytest tests/test_diary_template.py tests/test_diary_roster.py tests/test_booking_create_edit.py tests/test_slots.py -q plus any new focused tests; git diff --check.

## Merge Criteria

Room 2/Nurse can be represented as a practitioner-backed roster/template column in dev data; relevant API responses expose practitioner_id/AHPRA where needed; appointment/slots tests remain green; any remaining limitation around non-practitioner resource bookings is recorded.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
