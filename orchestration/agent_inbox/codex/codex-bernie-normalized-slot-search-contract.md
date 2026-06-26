# codex-bernie-normalized-slot-search-contract

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-normalized-slot-search` |
| Branch | `codex/bernie-normalized-slot-search` |
| Status | submitted |
| Created | 5ddd104 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-normalized-slot-search-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-normalized-slot-search-contract --commit-message "Bernie normalized slot search contract" --message "codex-bernie-normalized-slot-search-contract ready for Codex review"` |

## Mission

Plan first, then after Ariadne approval add a backend-only non-mutating endpoint or route helper that accepts SlotSearchCommandIn, requires explicit reference_date, normalizes it, and when safe runs the existing slot-search proposal path to return candidate slots plus normalization context for future Bernie/reception use.

## Scope

### In Scope

Plan packet first; after approval app/routers/appointments.py, app/schemas/appointments.py, app/services/bernie_slot_normalizer.py only if needed, and focused tests. Preserve deterministic reference-date handling. For unsafe normalization, return blocks without executing slot search. For safe normalization, reuse existing non-mutating slot-search proposal logic rather than duplicating scheduling rules. Include authentication/role behaviour consistent with adjacent slot-search endpoints and tests for response shape, invalid input, no appointment/audit writes, no LLM calls, and compatibility with existing SlotSearchProposalIn/SlotSearchProposalOut.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, appointment creation/edit/status/cancel, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, DB-backed name-to-UUID resolution, broad scheduling redesign, and any master/handoff push.

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

Plan packet first. After approval run py_compile on touched backend modules/tests, focused pytest for the new endpoint/helper, existing tests/test_bernie_slot_normalizer.py, existing tests/test_slot_search_normalize_endpoint.py, adjacent tests/test_slot_search_proposal.py if router/schema changes touch it, explicit no-mutation/no-LLM proof, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, Worker Branch codex/bernie-normalized-slot-search, clear backend-only scope, deterministic reference-date semantics, unsafe-command no-search behaviour, safe-command reuse of the existing non-mutating proposal path, and verification evidence. Implementation must not create/update appointments, write audit rows, call LLMs, or change frontend/UI behaviour.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/routers/appointments.py`, `app/schemas/appointments.py`, `tests/test_slot_search_normalized_execution.py`, `orchestration/agent_inbox/codex/codex-bernie-normalized-slot-search-contract.md`.
- Verification run: `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_slot_search_normalized_execution.py tests\test_bernie_slot_normalizer.py tests\test_slot_search_normalize_endpoint.py tests\test_slot_search_proposal.py`; `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_slot_search_normalized_execution.py tests\test_bernie_slot_normalizer.py tests\test_slot_search_normalize_endpoint.py tests\test_slot_search_proposal.py -q --tb=short -p no:randomly` (65 passed); `git diff --check`.
- Remaining risks: New route name is `/api/v1/appointments/proposals/slot-search/normalized`; Ariadne may prefer a different final naming convention. Explicit no-mutation/no-LLM proof: new endpoint test asserts safe search leaves `Appointment` and `AppointmentAuditLog` row counts unchanged; unsafe command monkeypatches `_build_slot_search_proposal` to raise if called and confirms blocked normalization returns no proposal; source inspection test asserts the endpoint contains no `generate_content`, `Gemini`, `db.add`, `db.commit`, or `_write_audit` calls. Existing proposal/no-mutation and normalize/no-LLM tests also passed.
