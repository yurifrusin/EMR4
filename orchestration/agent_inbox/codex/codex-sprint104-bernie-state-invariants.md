# codex-sprint104-bernie-state-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint104-bernie-state-invariants` |
| Status | submitted |
| Created | 12fb780 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint104-bernie-state-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint104-bernie-state-invariants --commit-message "Sprint 104 Bernie State Invariants" --message "codex-sprint104-bernie-state-invariants ready for Codex review"` |

## Mission

As a separate Codex worker, plan the Sprint 104 statechart/invariant and acceptance-harness layer for Bernie conversational memory. This is a read/plan-gated packet only; write and submit the implementation plan, then stop.

## Scope

### In Scope

Plan packet first only. Inspect current Bernie backend/UI/tests and propose invariants, transition tables, fixtures, and review-harness additions for conversational state memory. Cover turn history, immutable request reference date, visible diary page context, patient recognition versus details verification, patient_booking_context freshness, candidate snapshot ownership, stale proposal rules, no-slot states, and confirmation evidence.

### Out of Scope

Production code before plan approval; acting as Ariadne/orchestrator; broad root-to-branch API rewrite; XState/runtime dependency; backend context implementation; Diary UI implementation; live provider/browser manual testing; voice/headset/Caller ID; Medicare/HI/IHI/PVM/OPV; limited auto-mode implementation.

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

Plan must include concrete invariants, a transition table or statechart sketch, fixture scenarios from recent live tests, required backend/UI test names, resubmission criteria for worker plans, and acceptance gates proving no stale prompt/date/candidate/proposal reuse.

## Merge Criteria

Ariadne can accept the plan if it independently tightens Sprint 104 acceptance criteria, catches cross-branch state risks before implementation release, avoids overlapping production ownership, and preserves the agreed architecture decisions for future API-spine extraction.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- `tests/test_bernie_sprint104_state_memory.py` new implementation-neutral pytest harness for Sprint 104 state-memory invariants.
- `orchestration/agent_inbox/codex/codex-sprint104-bernie-state-invariants.md` status/completion notes only.
- Verification run: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe C:\Users\sarashera\emr4\scripts\agent_worktrees.py handin --agent codex` from `C:\Users\sarashera\EMR4-worktrees\codex` on `codex/sprint104-bernie-state-invariants`: succeeded, fetched origin and printed protocol alerts/task packet.
- Verification run: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe C:\Users\sarashera\emr4\scripts\agent_worktrees.py claim --agent codex --task codex-sprint104-bernie-state-invariants --status in_progress` from `C:\Users\sarashera\EMR4-worktrees\codex` on `codex/sprint104-bernie-state-invariants`: succeeded.
- Verification run: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_sprint104_state_memory.py -q`: passed, 8 tests.
- Verification run: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_transition_table.py -q`: passed, 5 tests.
- Verification run: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile tests\test_bernie_sprint104_state_memory.py`: passed.
- Verification run: `git diff --check`: passed.
- Verification attempted: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_transition_table.py tests/test_bernie_sprint100_state_contract.py -q`: `tests/test_bernie_transition_table.py` passed, but `tests/test_bernie_sprint100_state_contract.py` errored at setup because the shared test database schema was missing after an earlier `Base.metadata.drop_all` deadlock (`relation "practices" does not exist`). No production code was changed to repair this because the Sprint 104 Codex worker scope is invariant/review harness, not backend database fixture ownership.
- Remaining risks: This harness is an executable invariant spec, not the backend/UI implementation; Claude and Antigravity still need to bind their runtime outputs to these shapes. Sprint 104 should still ensure backend-owned freshness ids/hashes for confirmation evidence, avoid dual truth between `BernieSession` and legacy globals, keep `patient_booking_context` compact/deterministic, and preserve typed no-slot suggestions rather than prompt-string shortcuts.
