# codex-sprint-r4-deepseek-adversarial-past-date-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint-r4-past-date-review` |
| Status | superseded |
| Created | 20a420f |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r4-deepseek-adversarial-past-date-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r4-deepseek-adversarial-past-date-review --commit-message "Sprint R4 DeepSeek adversarial past-date review" --message "codex-sprint-r4-deepseek-adversarial-past-date-review ready for Codex review"` |

## Mission

Use a second DeepSeek Flash worker as an adversarial reviewer/test designer for backdated-date safety: identify bypasses, add or propose focused regression tests, and avoid overlapping production edits unless the implementation lane misses a critical small fix.

## Scope

### In Scope

Read app/services/bernie_slot_normalizer.py, app/routers/appointments.py, tests around Bernie normalizer/supervised booking; add a separate review/test artifact or focused test module if useful.

### Out of Scope

Do not refactor production broadly; do not alter diary UI; do not duplicate the implementation lane's production edits unless reporting a blocker; no live provider calls.

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

py_compile any new tests; run focused pytest for new adversarial tests and adjacent normalizer/supervised tests if possible; git diff --check.

## Merge Criteria

Provides independent evidence that past-date requests cannot reach executable slot search/proposal states, or documents concrete remaining risks for Ariadne integration.

## Completion Notes

- Superseded by Ariadne integration: the branch's pre-fix adversarial probes expected the old fail-open behavior and were not merged as tests.
- Useful findings were folded into R4's route-level regressions and closeout notes.
- Follow-up retained: direct raw appointment mutation and create-proposal temporal policy are outside Bernie's new-booking slot-search guard and should be addressed only after product-policy confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
