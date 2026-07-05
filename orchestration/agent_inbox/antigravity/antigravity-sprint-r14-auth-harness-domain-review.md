# antigravity-sprint-r14-auth-harness-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 8625209 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r14-auth-harness-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r14-auth-harness-domain-review --commit-message "Sprint R14 Gemini auth harness domain review" --message "antigravity-sprint-r14-auth-harness-domain-review ready for Codex review"` |

## Mission

Plan then review R14 auth bootstrap guard from receptionist workflow and test-design perspective, ensuring the guard clarifies harness auth failures without hiding real expired-session UX concerns.

## Scope

### In Scope

docs/receptionist_review_r14.md only after plan approval. Review expected staff workflow impact, expired-session UX risk, and acceptance checks for smoke-auth guard.

### Out of Scope

Production code, test implementation, backend routes, live provider/Office/GitHub Pages, and R12 reason-code assets.

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

Document-only artifact; confirm only docs/receptionist_review_r14.md changed.

## Merge Criteria

Ariadne has a concise Gemini review artifact for the auth harness guard and any follow-up UX concern.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - docs/receptionist_review_r14.md
- Verification run:
  - Confirmed creation of docs/receptionist_review_r14.md.
  - Verified that only docs/receptionist_review_r14.md is untracked/modified in the git repository.
- Remaining risks:
  - Test framework authentication setup relies on a valid `REVIEW_AUTH_TOKEN` environment variable. If that token expires or is misconfigured, tests will fail immediately at startup with an authentication error, which is the intended fail-fast behavior.
