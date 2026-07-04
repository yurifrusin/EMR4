# antigravity-sprint-d5-gemini-domain-policy-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 1fce3b7 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-d5-gemini-domain-policy-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-d5-gemini-domain-policy-review --commit-message "Sprint D5 Gemini domain policy review" --message "antigravity-sprint-d5-gemini-domain-policy-review ready for Codex review"` |

## Mission

Use Antigravity/Gemini as an independent backend/domain-policy reviewer for D5, not a UI lane. Review whether search_horizon should be threaded in the route/frame builder and what invariants/tests should protect it.

## Scope

### In Scope

Read D4 changes, _build_bernie_reception_context, slot search proposal flow, diary frames/policy/outcomes, and relevant tests. Produce a tangible review artifact under orchestration/agent_inbox/codex or the source packet completion notes. You may propose or implement a tiny non-overlapping test-only patch if clearly useful, but default to review/test-design.

### Out of Scope

No UI/frontend. No GraphRAG. No persisted sessions/migrations. No broad rewrite. Do not change outcome semantics or staff-facing copy.

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

If code is changed: py_compile touched files, focused pytest, git diff --check. If review-only: cite exact files/tests and concrete acceptance criteria.

## Merge Criteria

Ariadne can use the review if it is concrete, file-grounded, and either submits a repo artifact or leaves clear completion notes; stdout alone is not sufficient.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
