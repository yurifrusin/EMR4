# codex-sprint-v1-bernie-voice-and-tool-intent-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | e14568c |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-v1-bernie-voice-and-tool-intent-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-v1-bernie-voice-and-tool-intent-invariants --commit-message "Sprint V1 Bernie voice and tool-intent invariants" --message "codex-sprint-v1-bernie-voice-and-tool-intent-invariants ready for Codex review"` |

## Mission

Plan adversarial invariants for Bernie reception voice and typed tool-intent routing: model wording, retrieved facts, or user-suggested actions may propose or explain but must not directly mutate diary state, create confirm authority, or fabricate appointment-edit evidence.

## Scope

### In Scope

tests around Bernie/Diary state, proposal/confirm gates, appointment update/extend proposals, practice-knowledge/advisory frames, and Diary review harness if UI consumes typed intents; plan only until approved.

### Out of Scope

Production code before approval; broad API rewrite; persisted PHI/session tables; direct auto-mode writes; clinical scribe/consultant retrieval.

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

Adversarial tests for no direct writes, no confirm bypass, stale proposal rejection, authorship/source separation, and UI non-authority; py_compile/node checks as applicable.

## Merge Criteria

Plan accepted by Ariadne; invariant plan must name authority boundaries and failure modes before implementation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  `orchestration/agent_inbox/codex/plan-codex-codex-sprint-v1-bernie-voice-and-tool-intent-invariants.md`;
  `orchestration/agent_inbox/codex/codex-sprint-v1-bernie-voice-and-tool-intent-invariants.md`
  status/completion notes only.
- Verification run:
  Plan-gated only; no production code, tests, runtime docs, or runtime assets
  edited. Protocol handin completed with `py -3 scripts\agent_worktrees.py handin`
  after the Windows `python` app-execution alias failed. Read `AGENTS.md`,
  `orchestration/parallel_workstreams.md`, and the queued task packet.
- Remaining risks:
  Implementation not started. The eventual implementation must still prove no
  direct writes, no confirm bypass, stale proposal rejection, authorship/source
  separation, and UI non-authority with focused tests/checks.
