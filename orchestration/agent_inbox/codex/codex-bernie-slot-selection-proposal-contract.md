# codex-bernie-slot-selection-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-slot-selection-proposal` |
| Branch | `codex/bernie-slot-selection-proposal` |
| Status | queued |
| Created | 8f4153e |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-slot-selection-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-slot-selection-proposal-contract --commit-message "Bernie slot selection proposal contract" --message "codex-bernie-slot-selection-proposal-contract ready for Codex review"` |

## Mission

Plan first, then after Ariadne approval add a backend-only supervised contract for selecting one candidate returned by the normalized slot-search flow and converting that selection into existing appointment-create proposal input/evidence without creating an appointment, writing audit rows, calling LLMs, or changing UI.

## Scope

### In Scope

Plan packet first; after approval a narrow backend route/helper/schema/test slice in the appointments proposal area; accept a normalized search execution result or explicit candidate selection plus required appointment-create fields; validate candidate/date/time/duration/practitioner/location/patient constraints; return a non-mutating create-proposal-compatible payload or blocks/warnings for staff review; keep all appointment creation/confirmation out of scope; prove no appointment/audit writes and no LLM calls.

### Out of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous tool execution, actual appointment creation/edit/status/cancel, audit mutation, SMS, billing, patient demographics, resource admin, migrations unless strictly unavoidable, DB-backed natural-language name resolution, and broad scheduling redesign.

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

Plan packet first. After approval run py_compile on touched backend modules/tests, focused pytest for the new selection/review contract, adjacent slot-search normalized/proposal tests and appointment-create proposal tests if shared code changes, explicit no-mutation/no-LLM proof, and git diff --check.

## Merge Criteria

Plan packet includes Role codex-worker, Worker Name Cicero, Worker Branch codex/bernie-slot-selection-proposal, backend-only scope, supervised selection semantics, no appointment creation, no audit writes, no LLM calls, and verification evidence. Implementation must preserve existing normalized slot-search and create-proposal route compatibility.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
