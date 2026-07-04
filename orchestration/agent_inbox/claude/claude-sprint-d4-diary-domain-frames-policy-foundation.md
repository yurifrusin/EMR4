# claude-sprint-d4-diary-domain-frames-policy-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | 8f0468b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d4-diary-domain-frames-policy-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d4-diary-domain-frames-policy-foundation --commit-message "Sprint D4 diary domain frames policy foundation" --message "claude-sprint-d4-diary-domain-frames-policy-foundation ready for Codex review"` |

## Mission

Plan and then, after Ariadne approval, implement a narrow backend diary-domain sprint that strengthens Bernie as a native diary-domain receptionist copilot. Focus on existing app/services/diary frames, policy, outcomes, patient booking context, roster/schedule explanation, and tests. The sprint must avoid UI changes and avoid GraphRAG/persisted-session/broad API rewrites.

## Scope

### In Scope

Read existing app/services/diary modules and Bernie compatibility facades; identify the smallest missing domain-layer capability that addresses Yuri's recent concern: future patient bookings should be advisory unless same requested day/window, roster/schedule unavailability should explain itself, and no-candidates copy must only be allowed after a real slot search. Propose concrete files/tests, then wait at the plan gate.

### Out of Scope

No frontend/taskpane/diary.js changes. No GraphRAG/vector store. No persisted Bernie database sessions. No broad API review. No Fable/high-cost model unless explicitly requested. No master/handoff movement.

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

Focused pytest for the diary-domain policy/outcome/frame tests plus any new tests; py_compile touched files; git diff --check.

## Merge Criteria

Ariadne can integrate only if the change is backend-domain bounded, preserves current API contracts, strengthens typed frame/policy semantics, and has passing focused tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
