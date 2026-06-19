# codex-status-mutation-review-plan

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/status-mutation-review-plan` |
| Status | queued |
| Created | ea0b41d |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-status-mutation-review-plan --commit-message "Add status mutation review plan" --message "Status mutation review plan ready for Codex review"` |

## Mission

Prepare the integration and user-review checklist for controlled appointment status mutation before booking edit work begins.

## Scope

### In Scope

Documentation/checklist only. Inspect orchestration/patient_flow_review.md, orchestration/sprint_closeout.md, orchestration/parallel_workstreams.md, the appointment status route/tests, and diary status UI expectations. Add or update a small orchestration checklist that defines the post-integration review path for status mutation: API checks, diary UI checks, waiting-room behavior, failure/session handling, and what remains out of scope. Fill Completion Notes before submit.

### Out of Scope

No production backend/frontend implementation, no tests, no migrations, no taskpane/Command Centre/Gemini changes, no booking create/edit/drag/drop work.

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

Run git diff --check. No JS/Python test required unless implementation files are touched. Completion Notes must include the exact manual review checklist Codex should use after integrating Claude and Antigravity.

## Merge Criteria

Codex has a concise review checklist for status mutation controls; user review criteria are explicit; no production behavior changes are introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
