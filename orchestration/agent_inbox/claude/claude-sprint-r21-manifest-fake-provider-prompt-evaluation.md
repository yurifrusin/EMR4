# claude-sprint-r21-manifest-fake-provider-prompt-evaluation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 4b147aa |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r21-manifest-fake-provider-prompt-evaluation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r21-manifest-fake-provider-prompt-evaluation --commit-message "Sprint R21 Manifest fake-provider prompt evaluation" --message "claude-sprint-r21-manifest-fake-provider-prompt-evaluation ready for Codex review"` |

## Mission

Implement a fake-provider-only evaluation harness for the Bernie Diary Capability Manifest prompt block. Use render_manifest_prompt_block()/build_manifest_prompt_context() to assemble deterministic prompt inputs and prove via fake provider/tests that schema literacy instructions do not grant write authority, leak PHI, or bypass backend confirmation. No live Gemini calls.

## Scope

### In Scope

app/services/diary/capability_manifest.py, app/services/ai fake-provider/test-adjacent contracts if useful, tests for manifest prompt assembly/evaluation, orchestration docs.

### Out of Scope

Live Gemini/Vertex calls, production prompt wiring, frontend/Diary UI, database migrations, raw appointment mutations, PHI/log ingestion, broad AI provider refactor.

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

Run py_compile and focused pytest proving fake-provider prompt assembly is deterministic, non-live, audit-safe, no write-authority claims, and refusal-rule cases are represented without provider calls.

## Merge Criteria

Ariadne can integrate a fake-only evaluation seam that is safe to run in CI and still does not wire live Bernie prompt consumption.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
