# antigravity-sprint-n1b-diary-boundary-review-harness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | c3385e4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-n1b-diary-boundary-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-n1b-diary-boundary-review-harness --commit-message "Sprint N1b diary boundary review harness" --message "antigravity-sprint-n1b-diary-boundary-review-harness ready for Codex review"` |

## Mission

Plan and implement the N1b contract-review lane: adversarial availability provenance and suggestion-cannot-mutate tests around the new diary action envelopes/authorship metadata.

## Scope

### In Scope

Test/review harness ownership: tests for evaluate_reception_context proving advisory/model frames cannot fabricate availability classifications or unblock confirmation; tests proving DiaryActionSuggestion has no write authority; catalog authorship/completeness review; no UI changes. Coordinate with Claude/Ariadne if envelope names differ.

### Out of Scope

No service implementation beyond tests unless explicitly needed after plan acceptance; no UI/copy/routes/migrations/GraphRAG/persisted sessions/unified confirm path.

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

Plan packet first. Later implementation should run focused new tests, existing N1a compatibility tests, and git diff --check.

## Merge Criteria

Bounded adversarial/contract test lane that proves N1b's safety boundaries without runtime behaviour changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Ariadne integrated Antigravity's additional envelope-boundary
  test into `tests/test_diary_action_envelopes.py`.
- Verification run: focused N1b contract suite, compileall, focused
  `reception_policy` smoke checks, and `git diff --check` passed.
- Remaining risks: none for this bounded review lane.
