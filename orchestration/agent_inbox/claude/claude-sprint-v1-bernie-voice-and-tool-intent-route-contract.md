# claude-sprint-v1-bernie-voice-and-tool-intent-route-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | e14568c |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-v1-bernie-voice-and-tool-intent-route-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-v1-bernie-voice-and-tool-intent-route-contract --commit-message "Sprint V1 Bernie voice and tool-intent route contract" --message "claude-sprint-v1-bernie-voice-and-tool-intent-route-contract ready for Codex review"` |

## Mission

Plan the backend/domain contract for Bernie reception voice and typed tool-intent routing, starting with non-booking diary requests such as extending an existing appointment duration while preserving deterministic diary commands and staff confirmation as the only write authority.

## Scope

### In Scope

app/services/bernie or app/services/diary intent/router/domain modules; app/routers/appointments.py non-mutating proposal seams; schemas for typed tool-intent envelopes; tests proving voice/model output cannot write directly or bypass existing proposal/confirm authority.

### Out of Scope

Implementing broad auto-mode; persisted PHI/session tables; Graph/vector store deployment; taskpane/Command Centre; broad API rewrite; direct booking/write execution from LLM text; clinical scribe/consultant agents.

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

Focused route/domain tests for typed intent classification and non-mutating proposals; confirm/write authority tests; py_compile; git diff --check.

## Merge Criteria

Plan accepted by Ariadne; implementation must keep model voice/advisory separate from deterministic command/proposal/write authority and include clear follow-up boundaries.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
