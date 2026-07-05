# codex-sprint-r21-deepseek-prompt-adversarial-evals

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 4b147aa |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r21-deepseek-prompt-adversarial-evals --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r21-deepseek-prompt-adversarial-evals --commit-message "Sprint R21 DeepSeek prompt adversarial evals" --message "codex-sprint-r21-deepseek-prompt-adversarial-evals ready for Codex review"` |

## Mission

DeepSeek Flash worker: add or design deterministic adversarial fake-provider tests for manifest prompt evaluation. Focus on prompts that ask Bernie to bypass confirmation, invent status/reason codes, leak raw manifest/source, or claim live availability. Work test-only unless Ariadne expands scope.

## Scope

### In Scope

tests around manifest prompt consumption/evaluation, app/services/diary/capability_manifest.py helper behavior, orchestration notes.

### Out of Scope

Live AI calls, production prompt wiring, frontend UI, database migrations, appointment route mutations.

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

Return focused pytest or precise test plan; run py_compile/pytest for touched tests.

## Merge Criteria

Ariadne receives independent adversarial coverage for fake-provider prompt evaluation without overlapping Claude's implementation files unnecessarily.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW: `tests/test_bernie_fake_provider_adversarial_prompt.py` — deterministic adversarial coverage for fake-provider manifest prompt evaluation.
- Verification run:
  - DeepSeek reported compileall clean, 21/21 new tests passing, and R20 manifest tests passing.
  - Ariadne repaired f-string quoting in the submitted test file, then ran focused and broader manifest pytest locally.
- Remaining risks:
  - Unicode homoglyph/confusable key normalization is not implemented yet; track as a follow-up if adversarial provider output can use confusable key names.
