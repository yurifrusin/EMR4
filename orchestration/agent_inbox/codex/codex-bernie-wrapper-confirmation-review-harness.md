# codex-bernie-wrapper-confirmation-review-harness

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-wrapper-confirmation-review-harness` |
| Branch | `codex/bernie-wrapper-confirmation-review-harness` |
| Status | integrated |
| Created | 5a2be9a |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-wrapper-confirmation-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-wrapper-confirmation-review-harness --commit-message "Dispatch Sprint 47 Bernie wrapper confirmation harness" --message "Sprint 47 dispatched to Codex worker"` |

## Mission

Add a deterministic backend review harness proving the Sprint 46 supervised Bernie wrapper's confirmation_ready evidence can be explicitly confirmed through the existing confirm-Bernie endpoint, while blocked/candidate-only paths remain non-mutating.

## Scope

### In Scope

Plan first. After approval, focused backend tests/review harness only unless a tiny production fix is required by a real contract gap. Exercise /appointments/proposals/bernie/supervised-booking followed by /appointments/proposals/create/confirm-bernie for explicit confirmed=true success, confirmed=false block, stale-conflict revalidation, candidate_selection_required no-write, blocked normalization no-write, no LLM/provider calls, and exactly-one appointment/audit write on success.

### Out of Scope

Diary UI, taskpane, Command Centre, natural-language parsing, autonomous runtime execution, new appointment write routes, schema redesign, migrations, SMS, billing, resource admin, broad appointment/audit redesign, and changing Sprint 40-46 route semantics unless the harness exposes a verified bug.

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

Plan packet first. After approval: py_compile touched tests/Python; focused new harness pytest; rerun tests/test_bernie_supervised_booking_wrapper.py, tests/test_bernie_confirm_create_proposal.py, tests/test_bernie_confirmed_flow_review_harness.py, and adjacent slot-search/selection/create-proposal tests if production code is touched; prove no-write before explicit confirmation, no-write on blocked/stale paths, exactly-one-write/audit on success, no-LLM proof, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-wrapper-confirmation-review-harness. Implementation is test-focused, deterministic, backend-only, no-LLM, no autonomous booking, preserves Sprint 40-46 contracts, and proves the wrapper-to-confirm handoff is safe before any UI/runtime surface.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `tests/test_bernie_wrapper_confirmation_review_harness.py`; `orchestration/agent_inbox/codex/codex-bernie-wrapper-confirmation-review-harness.md`
- Verification run: `python scripts\agent_worktrees.py handin --agent codex`; `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m py_compile tests\test_bernie_wrapper_confirmation_review_harness.py`; `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_wrapper_confirmation_review_harness.py -q` -> 7 passed; sequential rerun of `tests\test_bernie_supervised_booking_wrapper.py`, `tests\test_bernie_confirm_create_proposal.py`, and `tests\test_bernie_confirmed_flow_review_harness.py` -> 7 passed, 6 passed, 4 passed; `git diff --check`. An attempted parallel run of the three adjacent suites hit a PostgreSQL enum create race (`userrole` duplicate), then passed when rerun sequentially.
- Remaining risks: No production code changed. Adjacent slot-search/selection/create-proposal suites were not rerun because production code was untouched. Pytest still emits the existing `pytest_asyncio` unset loop-scope deprecation warning.
