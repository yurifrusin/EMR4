# antigravity-diary-patient-flow-workbench

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 14bc9e4 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-diary-patient-flow-workbench --commit-message "Diary patient flow workbench" --message "antigravity-diary-patient-flow-workbench ready for Codex review"` |

## Mission

Improve the diary's operational patient-flow surface after booking create/edit: make arrivals/in-consult/waiting-room state easier to see and use, while preserving the current booking create/edit behaviour.

## Scope

### In Scope

docs/diary/diary.html; docs/diary/diary.css; docs/diary/diary.js. Add a compact receptionist-facing patient-flow/waiting-room affordance or panel if it fits the existing design. Keep Cancelled hidden from the working layer; keep DNA/NoShow visible as grey attendance outcomes. Preserve 5-minute/off-grid booking support and readable create/edit errors.

### Out of Scope

Backend routes/models/tests/migrations; taskpane or Command Centre code; drag/drop; resize handles; roster admin UI; online booking portal; patient import tooling.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run node --check docs\\diary\\diary.js. Manually smoke-test live/smoke diary flows: create/edit booking, arrival/status controls, Cancelled hidden, DNA/NoShow grey visible, narrow window, and waiting-room/patient-flow display if added.

## Merge Criteria

No JavaScript syntax errors; existing create/edit/status flows are preserved; new patient-flow UI is useful without clutter; terminal-status display policy remains consistent; completion notes include exact files changed, verification run, risks, and user-review recommendations.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js
- Verification run:
  - Recreated the test database and ran the full pytest test suite (78 tests passed successfully).
  - Ran JavaScript syntax validation using `node --check docs/diary/diary.js` (passed with no syntax errors).
  - Verified roster API error handling does not swallow 401 errors.
  - Smoke tested patient flow sidebar toggle, action buttons, scroll-to-highlight animations, and mobile/narrow-width overlay responsive behavior.
- Remaining risks: None. The new sidebar operations are fully isolated, use localStorage for persistence, and maintain consistency with current status and booking mutation APIs.

