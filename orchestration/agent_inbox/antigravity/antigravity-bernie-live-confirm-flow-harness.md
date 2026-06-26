# antigravity-bernie-live-confirm-flow-harness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 3fb45bf |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-live-confirm-flow-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-live-confirm-flow-harness --commit-message "Dispatch Sprint 52 Bernie live confirm flow harness" --message "Sprint 52 dispatched: Bernie live-review confirm flow harness"` |

## Mission

Add a deterministic smoke-mode review harness proving the existing Bernie supervised-booking live adapter and the explicit confirm submit adapter work together end-to-end under route interception, without enabling ordinary live diary mode.

## Scope

### In Scope

review/test_diary_smoke.py plus docs/diary/diary.{html,css,js} only if a tiny selector/state hook is necessary. Add tests that load the smoke-gated Bernie live review path with the confirm adapter enabled, route-intercept supervised-booking and confirm-Bernie, verify the review renders from the supervised-booking response, verify no confirm POST before approval, verify explicit approval posts exactly the confirm payload with confirmed=true, and verify blocked/candidate/error paths do not write.

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

Plan packet first and stop. After approval: node --check docs\\diary\\diary.js if diary JS changes; python scripts\\check_frontend_versions.py if diary assets change; pytest review\\test_diary_smoke.py --junitxml=review\\diary-review.xml -q; prove both endpoints are route-intercepted/stubbed and no normal-mode exposure is introduced; git diff --check.

## Merge Criteria

Plan packet lands in Codex inbox first with no production code changes. Implementation remains deterministic and smoke/feature-gated, avoids live mutation, does not broaden normal-mode exposure, keeps existing Bernie review/live/confirm-adapter tests green, and confines changes to the review harness unless a minimal diary test hook is explicitly justified.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `review/test_diary_smoke.py`.
- Verification run: `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py --junitxml=review\diary-review.xml -q`; `git diff --check`.
- Remaining risks: Antigravity repeatedly returned no implementation after release and nudge; Ariadne completed the approved test-only harness directly to avoid stalling the sprint. The harness remains smoke/route-intercepted only and performs no live writes.
