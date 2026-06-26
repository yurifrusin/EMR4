# codex-bernie-supervised-review-payload-contract

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-supervised-review-payload` |
| Status | queued |
| Created | ec601fc |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-supervised-review-payload-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-supervised-review-payload-contract --commit-message "Dispatch Sprint 48 Bernie supervised review payload" --message "Sprint 48 dispatched to Codex worker"` |

## Mission

Add a deterministic backend contract that turns the supervised Bernie booking wrapper result into a stable staff-review payload suitable for a later UI, without autonomous writes or LLM calls.

## Scope

### In Scope

Plan first. After approval, backend schema/router/service/test changes only as needed to expose or include a compact staff-review payload for supervised booking outcomes: blocked, candidate_selection_required, and confirmation_ready. The payload should give a UI stable fields for headline/status, staff action required, selected/candidate slot summary, warning/evidence summary, confirmation readiness, and the exact confirm payload/evidence needed where appropriate. Preserve existing result discriminators and existing Sprint 40-47 contracts.

### Out of Scope

Diary UI, taskpane, Command Centre, natural-language parsing, Gemini/LLM/provider calls, autonomous execution, direct appointment writes outside explicit confirm-Bernie, migrations unless genuinely unavoidable, SMS, billing, resource admin, broad appointment redesign, and changing the confirm-Bernie write contract.

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

Plan packet first. After approval: py_compile touched Python/tests; focused new/updated Bernie supervised review payload pytest; rerun tests/test_bernie_supervised_booking_wrapper.py, tests/test_bernie_wrapper_confirmation_review_harness.py, tests/test_bernie_confirm_create_proposal.py, tests/test_bernie_confirmed_flow_review_harness.py as relevant; prove no-write/no-audit before confirmation, no-LLM proof, existing result discriminators preserved, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-supervised-review-payload. Implementation gives later UI a stable deterministic staff-review contract while preserving all existing Bernie safety boundaries, with focused and adjacent tests green.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
