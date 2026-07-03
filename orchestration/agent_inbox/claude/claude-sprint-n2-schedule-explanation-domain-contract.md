# claude-sprint-n2-schedule-explanation-domain-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 84f8c16 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n2-schedule-explanation-domain-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n2-schedule-explanation-domain-contract --commit-message "Sprint N2 schedule explanation domain contract" --message "claude-sprint-n2-schedule-explanation-domain-contract ready for Codex review"` |

## Mission

Plan and implement N2 backend/domain foundation: typed schedule explanation in the diary domain plus reason-code copy catalog support, preserving deterministic diary authority and no write-path changes.

## Scope

### In Scope

Add a read-only diary-domain schedule explanation contract/capability that can represent no roster row, practitioner day off/unavailable, outside-hours/request window, breaks-only windows, fully booked, elapsed same-day window, and true searched-no-candidates. Add deterministic copy catalog keyed by state/reason code for backend/UI consumption. Integrate with existing reception frames/policy only where additive and behaviour-preserving.

### Out of Scope

No GraphRAG/K1 knowledge substrate, no persisted sessions, no unified confirm path, no HMAC/evidence changes, no auto-mode, no booking write changes, no broad UI redesign.

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

Run focused diary/bernie domain tests, new schedule explanation/copy catalog tests, existing reception_policy smoke checks if UI contract affected, compileall, git diff --check.

## Merge Criteria

Typed schedule explanations and copy catalog are deterministic, read-only, tested, and ready for Diary UI consumption without scenario-specific message branches.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
