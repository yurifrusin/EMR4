# antigravity-bernie-confirm-submit-adapter

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 28ab39d |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-confirm-submit-adapter --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-confirm-submit-adapter --commit-message "Dispatch Sprint 51 Bernie confirm submit adapter" --message "Sprint 51 dispatched: Bernie supervised confirm submit adapter"` |

## Mission

Add the next smoke-gated Bernie review UI slice: an explicit staff-approval submit adapter that posts the existing staff_review confirm payload only after deliberate approval, while remaining disabled in normal diary mode.

## Scope

### In Scope

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, diary asset cache-busts, and the Antigravity task/review packets. Implement only a smoke/feature-gated path, e.g. smoke=true with an explicit Bernie confirm adapter flag. Use deterministic route-intercepted review tests for confirmation-ready success, no submit before approval, blocked/candidate states, error handling, and exact confirm payload shape.

### Out of Scope

Backend route/schema/model changes, database migrations, normal non-smoke live diary enablement, autonomous Bernie actions, Gemini/LLM calls, taskpane, Command Centre, billing/SMS/security console, patient demographics, resource admin, and any un-intercepted real confirm-Bernie write during tests.

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

Plan packet first and stop. After approval: node --check docs\\diary\\diary.js; python scripts\\check_frontend_versions.py; pytest review\\test_diary_smoke.py --junitxml=review\\diary-review.xml -q; prove confirm-Bernie is not called before explicit staff approval and is route-intercepted/stubbed in tests; git diff --check.

## Merge Criteria

Plan packet lands in Codex inbox first with no production code changes. Implementation remains smoke/feature-gated, deterministic, no normal-mode exposure, no live mutation in tests, exact approval gating is covered, existing Bernie review fixture/live-adapter tests remain green, and diff is limited to the agreed diary/review harness surface.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
