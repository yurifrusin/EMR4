# codex-bernie-confirmed-flow-review-harness

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-confirmed-flow-review-harness` |
| Branch | `codex/bernie-confirmed-flow-review-harness` |
| Status | queued |
| Created | 08fe298 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-confirmed-flow-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-confirmed-flow-review-harness --commit-message "Dispatch Sprint 45 Bernie confirmed flow harness" --message "Sprint 45 dispatched to Codex worker"` |

## Mission

Add a deterministic backend review harness for the full supervised Bernie path: normalize command, execute normalized slot search, select one candidate, confirm the create proposal, and assert exactly-one appointment/audit write only at the explicit confirmation step.

## Scope

### In Scope

Plan first. After approval, tests/review-harness code only unless a tiny compatibility fix is strictly required and reported. Cover the full backend Bernie flow from normalize/search/select through confirm-bernie. Prove pre-confirmation steps write no appointments/audits, failed confirmation writes nothing, success writes exactly one appointment and bounded audit evidence, and no Gemini/LLM/provider calls occur.

### Out of Scope

Diary UI, taskpane, Command Centre, live Bernie runtime, natural-language autonomous execution, new production endpoints, migrations, billing, SMS, resource admin, broad audit redesign, broad appointment redesign, and unrelated test hygiene.

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

py_compile touched Python; run the new full-flow harness; rerun tests/test_bernie_confirm_create_proposal.py, tests/test_bernie_slot_flow_review_harness.py, tests/test_slot_selection_proposal.py, tests/test_slot_search_normalized_execution.py, and tests/test_appointment_proposals.py; prove no-write before confirmation, no-write on blocked confirmation, exactly-one-write/audit on success, no-LLM/provider calls, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-confirmed-flow-review-harness. Implementation is deterministic, backend-test focused, cost-conscious, no UI/runtime expansion, no autonomous booking behavior, and preserves Sprint 40-44 contracts.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
