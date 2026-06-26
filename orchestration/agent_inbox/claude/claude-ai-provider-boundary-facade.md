# claude-ai-provider-boundary-facade

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | b22a794 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-ai-provider-boundary-facade --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-ai-provider-boundary-facade --commit-message "AI provider boundary facade" --message "claude-ai-provider-boundary-facade ready for Codex review"` |

## Mission

Plan, then after approval add the first thin EMR4-owned AI service boundary so future clinical and Bernie AI work depends on EMR4 contracts rather than provider SDK calls.

## Scope

### In Scope

Plan first. After approval: small backend-only scaffold around existing Gemini consultation/letter usage, likely app/services/ai/contracts.py, app/services/ai/service.py, app/services/ai/providers/gemini.py, and focused tests or fixtures proving output schema boundaries. Preserve current runtime behaviour unless the plan justifies a safe no-op wrapper refactor.

### Out of Scope

No provider switch, no LiteLLM integration, no prompt rewrite, no live Gemini credential work, no diary frontend, taskpane UI, Command Centre UI, Bernie runtime, migrations, or broad consultation/letter behaviour changes. Do not edit production code before the plan gate is approved.

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

Plan packet first. After approval: py_compile touched Python modules, focused pytest for any new AI contracts/tests, existing consultation/letter tests if touched and available, no live provider calls required, git diff --check.

## Merge Criteria

Codex can see a plan packet with clear contract boundaries and, after implementation approval, a minimal provider-boundary change that keeps Gemini behaviour stable, validates structured outputs where introduced, and does not spread provider SDK imports into new surfaces.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
