# claude-bernie-dev-review-fixture-route

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | pending_plan_review |
| Created | a390acc |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-dev-review-fixture-route --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-dev-review-fixture-route --commit-message "Dispatch Sprint 55 Bernie dev review fixture route" --message "Sprint 55 dispatched: Bernie dev review fixture route"` |

## Mission

Plan first, then after approval add a narrow backend-only non-PHI dev fixture source for Bernie supervised review payloads so the dev launcher/review panel can exercise realistic deterministic payloads without hand-authored Playwright route payloads.

## Scope

### In Scope

Plan packet first; after approval a dev/test-only route or fixture helper under the appointments proposal surface, response schema reuse where possible, non-PHI deterministic payloads for blocked/candidate/confirmation-ready states, explicit gating so production/default behaviour is unaffected, auth/practice scoping if exposed as an API route, no appointment/audit writes, no LLM/provider calls, and focused pytest coverage.

### Out of Scope

Diary UI changes, taskpane, Command Centre, live autonomous booking, production default exposure, real patient data, Gemini/LLM parsing, migrations unless strictly unavoidable, appointment write semantics, SMS, billing, resource admin, broad appointment router redesign, and unrelated test hygiene.

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

Plan packet first; after approval py_compile touched backend modules/tests, focused pytest for the dev fixture route/helper, adjacent Bernie supervised-booking/review payload tests where relevant, no-write/no-audit proof, no-LLM/provider proof, auth/practice/default-gating checks if route is exposed, and git diff hygiene.

## Merge Criteria

Ariadne can verify the fixture source is deterministic and non-PHI, default production paths remain unaffected, it cannot write appointments or audit rows, it does not call any LLM/provider surface, it is suitably gated for dev/test use, tests cover blocked/candidate/confirmation-ready payloads, and the branch submits through protocol with clean diff hygiene.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
