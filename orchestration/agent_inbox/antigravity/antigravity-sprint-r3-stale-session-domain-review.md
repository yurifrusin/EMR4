# antigravity-sprint-r3-stale-session-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | b146f15 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r3-stale-session-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r3-stale-session-domain-review --commit-message "Sprint R3: Stale Session Domain Review" --message "antigravity-sprint-r3-stale-session-domain-review ready for Codex review"` |

## Mission

Use Gemini as an independent receptionist-domain reviewer for stale-session/revision hardening. Define acceptance cases and dissent for stale browser tabs, two receptionists, correction-vs-clarification, intent switches, and safe failure copy.

## Scope

### In Scope

Reception scenario corpus notes, R2 clarification semantics, test-design artifacts, optional natural-language or fixture additions under tests/fixtures/bernie_scenarios if clearly useful, a concrete acceptance/review artifact for Ariadne.

### Out of Scope

Production backend implementation ownership, Diary visual redesign, Word/taskpane changes, live provider calls, master/handoff updates, broad UI copy rewrite, GraphRAG/indexer automation.

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

Plan packet first; after approval, fixture integrity tests if scenario files change; review artifact must list concrete stale-session acceptance cases, expected safe behavior, and any dissent/risks.

## Merge Criteria

Provides actionable domain acceptance criteria and/or bounded scenario artifacts that Ariadne can use to validate Claude/DeepSeek implementation; no production code changes unless explicitly approved after plan gate.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/receptionist_review_r3.md](docs/receptionist_review_r3.md)
  - [tests/fixtures/bernie_scenarios/stale_session_concurrency_conflict.yaml](tests/fixtures/bernie_scenarios/stale_session_concurrency_conflict.yaml)
  - [tests/fixtures/bernie_scenarios/stale_session_reload_blocking.yaml](tests/fixtures/bernie_scenarios/stale_session_reload_blocking.yaml)
  - [tests/fixtures/bernie_scenarios/stale_session_correction_and_pivot.yaml](tests/fixtures/bernie_scenarios/stale_session_correction_and_pivot.yaml)
- Verification run:
  - Ran `pytest tests/test_bernie_scenario_integrity.py` which passes successfully (8 passed, 1 skipped).
  - Ran `pytest tests/bernie_scenarios/ -v` which passes (1 passed, 1 xfailed).
- Remaining risks:
  - Concurrency checks must sync with WebSocket updates to prevent race conditions during intensive clinic operations.
  - The client must handle `stale_session_revision` errors carefully to preserve the user's uncommitted text input where possible.
