# antigravity-sprint-r6-temporal-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | d367b7f |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r6-temporal-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r6-temporal-domain-review --commit-message "Sprint R6 Gemini temporal domain review" --message "antigravity-sprint-r6-temporal-domain-review ready for Codex review"` |

## Mission

Use Antigravity/Gemini to provide domain and test-design review for Bernie temporal-boundary policy: same-day past windows, stale reference dates, absolute past dates, and receptionist-safe clarification versus hard block semantics.

## Scope

### In Scope

docs/receptionist_review_r6.md; classification of temporal boundary scenarios by clinical safety value and executable readiness; acceptance notes for future harness work.

### Out of Scope

Production code edits, broad harness rewrite, Diary UI, taskpane/Word assets, live provider calls, raw appointment mutation implementation.

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

Tangible review artifact with actionable temporal-boundary recommendations; existing scenario integrity should remain passable.

## Merge Criteria

Gemini review clearly states which temporal policies should be hard-blocked, clarified, or left memory-only, and how to test them deterministically.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - docs/receptionist_review_r6.md
- Verification run:
  - Verified docs/receptionist_review_r6.md exists and contains the safety rankings, semantic boundaries, deterministic test recommendations, and analysis of DeepSeek A1 edge case.
  - Verified git status shows only docs/receptionist_review_r6.md modified.
  - Verification run via python compile check on appointments.py was bypassed as no production files were changed.
- Remaining risks:
  - The interpret path route-level bug (A1) was verified by static analysis of appointments.py:L3718-3722 but will be implemented/fixed in a subsequent implementation lane.
