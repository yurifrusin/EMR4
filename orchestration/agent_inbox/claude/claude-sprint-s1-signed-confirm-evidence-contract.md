# claude-sprint-s1-signed-confirm-evidence-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 11cbb2c |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-s1-signed-confirm-evidence-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-s1-signed-confirm-evidence-contract --commit-message "Sprint S1 signed confirm evidence contract" --message "claude-sprint-s1-signed-confirm-evidence-contract ready for Codex review"` |

## Mission

Plan Sprint S1 backend/domain work to replace unsigned/optional Bernie candidate/proposal freshness evidence with server-signed HMAC evidence for confirmation-grade flows, preserving current behaviour until implementation is explicitly approved.

## Scope

### In Scope

Plan only first. app/services/bernie_turn_evidence.py, app/services/diary/confirm_gate.py only if needed for evidence shape, appointment proposal/confirm endpoints in app/routers/appointments.py, schemas/tests for signed candidate/proposal evidence, fail-closed missing/malformed/mismatched evidence for new grammar-routed confirms, compatibility strategy for legacy clients.

### Out of Scope

No implementation before plan gate, no persisted session table, no GraphRAG/retrieval wiring, no auto-mode, no broad raw appointment write-path redesign, no UI redesign, no production secret migration unless plan identifies it.

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

Plan packet first. Later implementation should run focused evidence/confirm/proposal pytest suites, existing Bernie confirm flow suites, compileall, git diff --check, and document any legacy compatibility path.

## Merge Criteria

Concrete low-risk plan for HMAC-signed confirmation evidence that makes confirm-grade writes fail closed without breaking ordinary current Bernie booking tests.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
