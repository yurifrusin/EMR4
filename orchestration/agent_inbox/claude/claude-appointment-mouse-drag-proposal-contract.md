# claude-appointment-mouse-drag-proposal-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | a9ef0bb |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-appointment-mouse-drag-proposal-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-appointment-mouse-drag-proposal-contract --commit-message "Dispatch Sprint 27 backend mouse proposal contract" --message "claude-appointment-mouse-drag-proposal-contract ready for Codex review"` |

## Mission

Plan and then, only after approval, harden the backend proposal/update contract for diary mouse drag/drop and resize-handle interactions so frontend pointer gestures use the same safe/warning/blocked semantics proven by keyboard shortcuts.

## Scope

### In Scope

Backend tests and minimal contract fixes only if a real gap is found: app/routers/appointments.py, app/schemas/appointments.py, tests/test_appointment_update_proposal.py or adjacent appointment proposal tests. Cover mouse-equivalent payloads for start-time move, duration resize, and resource/room column move through POST /appointments/proposals/update/{appointment_id} and the existing confirmed update path.

### Out of Scope

No diary frontend, no pointer UI, no new schema/migration unless a blocking contract bug is proven, no recurrence, no patient identity, no taskpane/Command Centre, no bypass of proposal-gated writes.

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

.venv\\Scripts\\python.exe -m py_compile app\\routers\\appointments.py app\\schemas\\appointments.py; .venv\\Scripts\\python.exe -m pytest tests\\test_appointment_update_proposal.py -q --tb=short -p no:randomly; git diff --check

## Merge Criteria

Plan packet submitted first. Implementation, if approved, preserves existing keyboard proposal behavior, proves mouse-equivalent move/resize/column-change payloads are safe or blocked correctly, and keeps changes minimal.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - `tests/test_appointment_conflicts.py` — added `_put` helper function and 4 new tests in a "PUT /{id} conflict enforcement" section. No production code changes.

- Verification run:
  - `pytest tests/test_appointment_conflicts.py -v --tb=short -p no:randomly` — **12 passed, 0 failed** (8 pre-Sprint-27 + 4 new)
  - New tests confirm the PUT /{id} write path rejects conflicting drag-move (409), resize-into-next (409), and cross-column practitioner drag (409), and allows adjacency (200).

- Remaining risks:
  - No implementation changes — zero blast radius on existing endpoints or schemas.
  - The adjacency test (`test_put_adjacent_drag_allowed`) encodes the same open-interval semantics on the write path that Sprint 26 proved on the proposal path. If `_overlaps` ever changes to closed-interval, both test suites catch it.
