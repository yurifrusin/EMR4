# antigravity-sprint-r17-expired-session-ux-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 4ad3bf6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r17-expired-session-ux-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r17-expired-session-ux-review --commit-message "Dispatch R17 expired-session UX review" --message "Sprint R17 expired-session UX review packet"` |

## Mission

Review the Diary expired-auth/session-expired user experience and propose a staff-safe visible banner/state that avoids a blank or ambiguous diary when the JWT is missing, locally expired, or a backend request returns 401.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and a tangible review artifact under docs/ naming exact copy, affordance, and smoke-test expectations.

### Out of Scope

Backend auth changes, login flow changes outside the Diary surface, real credentials, PHI, broad redesign of the Diary header/grid/flow panels, or changing appointment/status/reason-code semantics.

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

Inspect the current auth/token paths, reason about missing-token/local-expired/401 states, and write a concise docs/receptionist_review_r17.md artifact with recommended copy, selectors, risks, and acceptance checks.

## Merge Criteria

Ariadne can implement or verify the visible session-expired state from the artifact; the recommendation keeps staff safe, preserves smoke mode, and identifies deterministic checks.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `docs/receptionist_review_r17.md` captured the receptionist-domain review; Ariadne implemented the accepted visible banner and refresh-stop behaviour in the Diary surface.
- Verification run: Antigravity/Gemini inspected the auth/token paths and produced review guidance; Ariadne verified with focused and full deterministic Diary smoke tests.
- Remaining risks: Antigravity recommended richer connecting/unauthorized copy variants and offline-network handling; Sprint R17 intentionally kept one simple expired-session banner and explicit `401` handling.
