# codex-sprint-g5-status-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 40a0e33 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-g5-status-confirm-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-g5-status-confirm-invariants --commit-message "Sprint G5 status confirm invariants" --message "codex-sprint-g5-status-confirm-invariants ready for Codex review"` |

## Mission

Plan adversarial invariants for migrating status-only writes onto a signed status-confirm route, focusing on evidence purpose, current appointment state, waiting-area semantics, and no raw PATCH from signed-capable UI.

## Scope

### In Scope

Read-only invariant plan over app/schemas/appointments.py, app/routers/appointments.py, docs/diary/diary.js status-only paths, tests/test_appointment_status_mutations.py, tests/test_appointment_audit.py, tests/test_waiting_area_checkin_contract.py, review/test_diary_smoke.py. No production code during plan gate.

### Out of Scope

Create/edit detail confirms; cancel/delete; broad Bernie action grammar; persisted sessions; GraphRAG; taskpane; Command Centre; visual redesign.

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

Plan packet only during plan gate. Later implementation should include backend adversarial tests and deterministic Diary route-intercept smoke.

## Merge Criteria

Ariadne accepts the plan only if it lists concrete stale/tamper/cross-practice/waiting-area/no-status-after-failed-confirm cases and keeps raw PATCH bounded as compatibility only.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-sprint-g5-status-confirm-invariants.md` status/completion notes and `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g5-status-confirm-invariants.md` plan packet only. No production code edited.
- Verification run: Plan-gate intake completed with `C:\Users\sarashera\emr4\.venv\Scripts\python.exe C:\Users\sarashera\emr4\scripts\agent_worktrees.py handin --agent codex`; read `AGENTS.md`, `orchestration/parallel_workstreams.md`, task packet, and scoped status surfaces; created plan packet with `C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\agent_worktrees.py plan --agent codex --task codex-sprint-g5-status-confirm-invariants ...`. No backend/frontend tests run because this was plan-only.
- Remaining risks: Later implementation must preserve `waiting_area_id` omitted-vs-null semantics, keep status confirm evidence purpose distinct from create/update evidence, avoid raw PATCH from signed-capable Diary status paths while keeping raw PATCH compatibility bounded, and ensure failed confirms leave appointment state and audit rows unchanged.
