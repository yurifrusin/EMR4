# codex-sprint-r23-deepseek-adversarial-frame-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | c8fed3c |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r23-deepseek-adversarial-frame-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r23-deepseek-adversarial-frame-review --commit-message "Sprint R23 DeepSeek adversarial frame review" --message "codex-sprint-r23-deepseek-adversarial-frame-review ready for Codex review"` |

## Mission

Second DeepSeek Flash lane: independently review R22/R23 fake-provider frame validators for bypasses. Focus on safe-looking malformed proposal/clarify/refusal/read_request outputs, hidden patient IDs, reason-code defaults, availability assertions, and write flags.

## Scope

### In Scope

adversarial review artifact or non-overlapping tests around manifest_eval frame validation

### Out of Scope

Live AI calls, production prompt wiring, frontend UI, DB/migrations

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

Return focused pytest or precise test/review artifact; run py_compile/pytest if files are changed.

## Merge Criteria

Ariadne receives independent adversarial coverage without overlapping the implementation lane unnecessarily.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/r23_deepseek_adversarial_frame_review.md` plus Ariadne-integrated frame-shape tests in `tests/test_bernie_manifest_receptionist_scenarios.py`.
- Verification run: Adversarial recommendations were translated into focused frame-shape tests and the R23 manifest suite.
- Remaining risks: Expand from observed live-provider output only after safe dry-run sampling; no live mutation authority added.
