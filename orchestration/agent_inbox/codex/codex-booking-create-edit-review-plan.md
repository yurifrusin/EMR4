# codex-booking-create-edit-review-plan

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/booking-create-edit-review-plan` |
| Status | submitted |
| Created | 9ccd838 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-booking-create-edit-review-plan --commit-message "Booking create/edit review plan" --message "codex-booking-create-edit-review-plan ready for Codex review"` |

## Mission

Prepare the integration and user-review checklist for the first booking create/edit sprint so Codex can merge backend and diary UI work without losing the safety boundaries.

## Scope

### In Scope

orchestration/status or review documentation only, such as a focused booking create/edit review file and sprint closeout draft notes. Capture API commands the user can run directly in PowerShell.

### Out of Scope

Production backend/frontend code, migrations, tests beyond documentation syntax/diff checks, drag/drop/resize, roster admin UI, taskpane/Command Centre/Gemini.

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

git diff --check.

## Merge Criteria

Review notes clearly distinguish required user checks from optional checks; include exact PowerShell API snippets for create/edit/list/conflict checks; document what remains intentionally out of scope.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/booking_create_edit_review.md` added with Sprint 8 integration/user review checklist and exact PowerShell API snippets for login, ID discovery, create, edit, list, conflict, slots, and cancellation/non-blocking checks.
  - `orchestration/sprint_closeout.md` updated with a Sprint 8 closeout draft section that does not replace the current Sprint 7 closeout.
  - `orchestration/agent_inbox/codex/codex-booking-create-edit-review-plan.md` updated with these completion notes.
- Verification run:
  - `git diff --check` passed.
- Remaining risks:
  - PowerShell snippets are documented but not live-run in this docs-only worker because the packet only required diff syntax verification.
  - Snippets depend on a running local stack plus seeded dev data; if seed data changes and no seeded appointments exist, the checklist intentionally stops and asks the reviewer to rerun `python seed.py` or provide IDs.
  - Final merge should reconcile any API/UI contract changes from Claude or Antigravity before treating the checklist as authoritative.
