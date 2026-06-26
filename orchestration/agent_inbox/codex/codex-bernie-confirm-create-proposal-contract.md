# codex-bernie-confirm-create-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-confirm-create-proposal` |
| Branch | `codex/bernie-confirm-create-proposal` |
| Status | integrated |
| Created | 5bfc019 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-confirm-create-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-confirm-create-proposal-contract --commit-message "Dispatch Sprint 44 Bernie confirmation bridge" --message "Sprint 44 dispatched to Codex worker"` |

## Mission

Add the final supervised backend confirmation bridge that turns approved Bernie slot-selection/create-proposal evidence into an actual appointment write with explicit audit semantics.

## Scope

### In Scope

Plan first. After approval, a narrow backend appointment proposal confirmation slice only, likely app/routers/appointments.py, app/schemas/appointments.py, and focused tests. The bridge must consume already-supervised create-proposal evidence from the Sprint 42/43 chain, require explicit confirmation, create exactly one appointment when safe, preserve practice/auth/conflict checks, and write bounded audit evidence that identifies the supervised Bernie/proposal source.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous Bernie runtime, direct natural-language execution, SMS, billing, resource admin, migrations unless strictly unavoidable, broad appointment redesign, broad audit framework redesign, and unrelated test hygiene.

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

py_compile touched Python; focused confirmation/write pytest; rerun Sprint 43 flow harness and adjacent slot-selection/create-proposal tests; prove failed/blocked confirmation writes no appointment/audit rows; prove successful confirmation writes exactly one appointment and bounded audit evidence; prove no LLM/provider calls; git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-confirm-create-proposal; implementation is backend-only, explicit-confirmation-only, supervised, non-LLM, preserves existing proposal safety, and does not add UI or autonomous booking behavior.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/routers/appointments.py`, `app/schemas/appointments.py`, `tests/test_bernie_confirm_create_proposal.py`, plus this task packet's completion notes. Backend-only; no diary UI/taskpane/Command Centre files touched.
- Verification run: `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m py_compile app\routers\appointments.py app\schemas\appointments.py tests\test_bernie_confirm_create_proposal.py`; `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_confirm_create_proposal.py tests\test_bernie_slot_flow_review_harness.py tests\test_slot_selection_proposal.py tests\test_appointment_proposals.py -q` (21 passed; pytest-asyncio deprecation warning only); additional audit-warning regression `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_confirm_create_proposal.py tests\test_appointment_audit_warning_summary.py -q` (19 passed; same warning); `git diff --check`.
- Remaining risks: Audit source evidence is stored as bounded internal codes in the existing `appointment_audit_log.confirmed_warnings` JSONB field to avoid a migration; Ariadne may later choose a dedicated audit-evidence column if the audit model is broadened.
