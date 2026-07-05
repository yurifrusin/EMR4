# claude-sprint-r20-manifest-prompt-consumption-gate

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | e0406aa |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-r20-manifest-prompt-consumption-gate --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-r20-manifest-prompt-consumption-gate --commit-message "Sprint R20 Manifest prompt consumption gate" --message "claude-sprint-r20-manifest-prompt-consumption-gate ready for Codex review"` |

## Mission

Design and implement the first safe read-only consumption gate for Bernie Diary Capability Manifest v1. The gate should expose compact manifest context to future Bernie prompt assembly without PHI, credentials, executable code, or write authority, and should include deterministic tests proving safety boundaries.

## Scope

### In Scope

app/services/diary/capability_manifest.py, app/services/bernie or AI prompt-adjacent services only if an existing safe assembly point exists, tests around manifest payload/redaction/authority boundaries, orchestration docs.

### Out of Scope

Live Gemini calls, changing production prompts unless explicitly isolated behind a non-runtime helper/test path, database migrations, frontend/Diary UI changes, raw codebase dumping, PHI/log ingestion, autonomous writes.

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

Run py_compile and focused pytest proving manifest payload is JSON-serializable, compact, no PHI/live rows/credentials, read-only, and cannot grant writes. Include any prompt-consumption helper tests if implemented.

## Merge Criteria

Ariadne can integrate a safe non-mutating manifest-consumption boundary or a precise no-runtime-change scaffold before any live Bernie prompt use.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
