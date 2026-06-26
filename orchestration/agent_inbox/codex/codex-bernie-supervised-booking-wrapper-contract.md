# codex-bernie-supervised-booking-wrapper-contract

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-supervised-booking-wrapper` |
| Branch | `codex/bernie-supervised-booking-wrapper` |
| Status | queued |
| Created | 9ede142 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-supervised-booking-wrapper-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-supervised-booking-wrapper-contract --commit-message "Dispatch Sprint 46 Bernie supervised wrapper" --message "Sprint 46 dispatched to Codex worker"` |

## Mission

Add a thin backend-only supervised Bernie booking wrapper contract that composes the existing deterministic normalize, normalized slot-search, and slot-selection proposal behaviours into one non-mutating proposal/intake surface for future Bernie UI/runtime use.

## Scope

### In Scope

Plan first. After approval, a narrow backend API/schema/test slice only. The wrapper must accept typed deterministic command input, perform no LLM/Gemini/provider calls, write no appointments/audits, and return a discriminated response that either presents candidate slots for staff selection or returns create-proposal evidence ready for explicit confirmation through the existing confirm-bernie endpoint. Preserve existing auth/practice/conflict checks and reuse current helper logic wherever possible.

### Out of Scope

Diary UI, taskpane, Command Centre, natural-language parsing, autonomous runtime execution, direct appointment writes, confirmation writes, SMS, billing, resource admin, migrations unless strictly unavoidable, broad appointment redesign, and broad audit redesign.

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

py_compile touched Python; focused wrapper tests; rerun tests/test_bernie_confirmed_flow_review_harness.py, tests/test_bernie_confirm_create_proposal.py, tests/test_slot_search_normalized_execution.py, tests/test_slot_selection_proposal.py, and tests/test_appointment_proposals.py; prove wrapper is non-mutating, no-LLM/provider, practice/auth scoped, returns candidate-selection vs confirmation-ready responses correctly, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-supervised-booking-wrapper. Implementation is backend-only, non-mutating, no-LLM, no autonomous booking, preserves Sprint 40-45 contracts, and gives future Bernie UI/runtime one supervised proposal surface without bypassing explicit confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
