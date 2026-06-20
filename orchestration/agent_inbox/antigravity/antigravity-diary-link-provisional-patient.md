# antigravity-diary-link-provisional-patient

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | c96c637 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-link-provisional-patient --commit-message "Add diary provisional patient linking" --message "Diary provisional patient linking ready for Codex review"` |

## Mission

Add the receptionist-facing diary UI to link a provisional/free-text booking to an existing patient record from the booking modal, while keeping the current identity-warning behaviour for unlinked progression. Add a save-time warning when an appointment crosses a visible break block, but keep crossing breaks allowed after acknowledgement.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, cache-bust bump if diary assets change. Use existing patient search and appointment update APIs; add only frontend helpers needed for link/unlink display and break-crossing warning.

### Out of Scope

Backend routes/models/tests/migrations, taskpane/Command Centre, drag/drop/resize, SMS reminder workflow, billing/completion workflow, full waiting-area model, patient duplicate backend rules.

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

Run node --check docs\\diary\\diary.js, git diff --check, and smoke/live checks for provisional create, link existing patient, status warning, break-crossing warning, narrow layout, and failure paths. Include exact commands/results and observations in Completion Notes.

## Merge Criteria

Diary can convert a provisional booking into a linked-patient booking without re-creating the appointment; linked/provisional visual semantics remain clear; unconfirmed identity warnings still fire before Arrived/InConsult/Completed; break-crossing warning appears but does not hard-block; no backend files touched.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
