# codex-bernie-slot-normalize-endpoint-contract

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-slot-normalize-endpoint` |
| Status | integrated |
| Created | 73f6bf0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-slot-normalize-endpoint-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-slot-normalize-endpoint-contract --commit-message "Codex Bernie Slot Normalize Endpoint Contract" --message "codex-bernie-slot-normalize-endpoint-contract ready for Codex review"` |

## Mission

Act as Codex worker/subagent replacement for Claude while Claude is quota-limited. Plan first, then after Ariadne approval implement the Sprint 40 Bernie slot command normalization endpoint/route contract.

## Scope

### In Scope

Plan packet first; after approval add a non-mutating backend endpoint or route helper that accepts SlotSearchCommandIn, invokes normalize_slot_search_command with explicit deterministic reference-date handling, returns SlotSearchCommandResult, and adds focused tests for auth, response shape, invalid input, non-mutation, no DB writes, no LLM/search execution, and compatibility with SlotSearchProposalIn.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, appointment creation, slot-search execution beyond normalizer invocation, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, and DB-backed name-to-UUID resolution.

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

Plan packet first; after approval py_compile touched backend modules/tests, focused endpoint/route pytest, existing normalizer tests, adjacent slot-search proposal tests if schemas/routes are touched, non-mutation/no LLM proof, and git diff --check.

## Merge Criteria

Ariadne can verify the Codex worker branch is explicit, scoped, deterministic, non-mutating, covered by focused tests, compatible with the Sprint 38/39 Bernie pipeline, and does not alter visible UI or live appointment creation behavior.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/routers/appointments.py`, `tests/test_slot_search_normalize_endpoint.py`, Sprint 40 Codex plan/review packets, and orchestration closeout/log/board records.
- Verification run: `python -m py_compile app\routers\appointments.py app\schemas\appointments.py app\services\bernie_slot_normalizer.py tests\test_slot_search_normalize_endpoint.py`; `python -m pytest tests\test_slot_search_normalize_endpoint.py tests\test_bernie_slot_normalizer.py tests\test_slot_search_proposal.py -q --tb=short -p no:randomly` -> 58 passed; `git diff --check` -> passed.
- Remaining risks: None for Sprint 40. Later Bernie slices still need supervised UI/tool wiring and a product decision on whether non-mutating normalization should be available to any authenticated staff role or only appointment-mutating staff roles.
