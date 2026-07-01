# antigravity-sprint97-bernie-ui-readiness

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 89fb530 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint97-bernie-ui-readiness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint97-bernie-ui-readiness --commit-message "Sprint 97 Bernie UI readiness and honest failure UX" --message "antigravity-sprint97-bernie-ui-readiness ready for Codex review"` |

## Mission

Plan the diary UI adjustments needed so Bernie feels like a helpful receptionist assistant while honestly handling interpreter readiness, deterministic fallback, candidate selection, and confirm-only booking.

## Scope

### In Scope

Plan packet first only. Inspect docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and Sprint 96 closeout. Propose exact UI copy and state handling for ready, searching, candidate-list, selected provisional slot, confirm-ready, and provider-unavailable/fallback states. Include how to avoid scary/internal wording while still making setup failures visible to developers.

### Out of Scope

Production code edits before plan approval; backend/schema/provider changes except documented requested contracts; live phone/Medicare/provider integrations; taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, and any direct booking write before staff confirmation.

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

Plan must name exact diary files/tests to touch, route-intercepted versus real-backend smoke distinctions, keyboard confirm checks, provisional-slot pulse/readability checks, asset version checks, and failure signs for provider readiness.

## Merge Criteria

Ariadne can approve only if ordinary reception mode never tells staff to use raw structured IDs, developer-only diagnostics stay hidden unless requested, and UI tests distinguish mocked UI contract from true backend/live readiness.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html, review/test_diary_smoke.py
- Verification run: Ran Playwright test suite using .venv\Scripts\pytest.exe review/test_diary_smoke.py (all 57 tests passed successfully).
- Remaining risks: None. The implementation uses standard DOM utilities, restricts setup diagnostics to dev review/debug mode, and handles fallback states cleanly.
