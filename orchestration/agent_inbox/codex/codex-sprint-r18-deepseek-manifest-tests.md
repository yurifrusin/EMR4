# codex-sprint-r18-deepseek-manifest-tests

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 379d0df |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r18-deepseek-manifest-tests --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r18-deepseek-manifest-tests --commit-message "Dispatch R18 DeepSeek manifest tests" --message "Sprint R18 DeepSeek manifest tests packet"` |

## Mission

DeepSeek Flash worker: design deterministic tests for a read-only Bernie Diary Capability Manifest v1 so it stays schema-literate, source-grounded, and non-authoritative. Work read-only unless Ariadne explicitly asks for edits.

## Scope

### In Scope

tests around app/services/diary and app/services/bernie, orchestration docs, possible manifest artifact path, pytest conventions.

### Out of Scope

Live AI tests, prompt evaluation, GraphRAG/MCP indexing, migrations, runtime Gemini calls, or frontend changes.

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

Return a test plan with specific pytest checks: manifest schema validity, no write-authority claims, source constant coverage, allowed/blocked transition examples, and golden text stability.

## Merge Criteria

Ariadne receives a deterministic test plan that can be implemented without live AI or broad fixture setup.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none by worker; Ariadne implemented the deterministic manifest suite in `tests/test_bernie_diary_capability_manifest.py`.
- Verification run: test design accepted for source parity, frozen/unique registry entries, staff-only confirm capabilities, non-confirm no-write claims, outcome coverage, and confirmation-envelope write boundary.
- Remaining risks: keep count assertions source-derived rather than brittle; add drift tests for frontend outcome copy in the next sprint before prompt injection.
