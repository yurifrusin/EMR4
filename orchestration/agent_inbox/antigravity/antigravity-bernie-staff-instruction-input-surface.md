# antigravity-bernie-staff-instruction-input-surface

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 3cfbc49 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-staff-instruction-input-surface --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-staff-instruction-input-surface --commit-message "Dispatch Bernie staff instruction input surface" --message "Plan for gated Bernie staff instruction input surface"` |

## Mission

Plan first, then after approval add a proper staff-entered booking-instruction input surface for the gated Bernie pilot review flow so staff can type a non-PHI operational instruction without using URL query strings or browser history.

## Scope

### In Scope

Plan packet first. After approval, docs/diary UI assets and review/test harness only as needed; a compact staff instruction input inside the existing Bernie pilot/review launch path; submit instruction text to the existing interpret/review request body only; no free-text query parameters, no localStorage persistence of instruction text, no automatic live-provider call before explicit staff action, clear empty/clarification/blocked states, preserve existing pilot/context/approval gates, route-intercepted Playwright checks for default hidden/no-call, body-only instruction submission, clarification blocked from confirm, and existing confirmation-ready approval gating; bump frontend asset versions if runtime assets change.

### Out of Scope

Backend routes/schemas/provider changes, autonomous booking, production default exposure without the existing pilot gates, PHI-heavy logging or persistence, query-string instruction intake, patient/practitioner selector redesign, taskpane, Command Centre, migrations, billing, SMS, resource admin, broad diary redesign, and unrelated refactors.

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

Plan packet first. After approval run node --check docs/diary/diary.js, focused route-intercepted review harness checks for the staff instruction input surface, the full diary review harness if diary runtime assets change, frontend version integrity checks, and git diff --check.

## Merge Criteria

Codex can merge when the plan is accepted, implementation stays within diary/review assets, default diary and non-pilot modes make no interpret/confirm calls, staff-entered text is never accepted through URL/query/localStorage, the instruction is sent only in an authenticated POST body after explicit staff action, confirm-Bernie remains impossible until the existing explicit approval checkbox path, and deterministic checks pass.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `docs/diary/diary.html` (Lines 129–141): Added the static structure for `#bernie-instruction-container`, `#bernie-instruction-input`, and `#btn-bernie-instruction-submit`.
  - `docs/diary/diary.css` (Lines 2639–2685): Appended styles for the staff instruction textarea and submit button.
  - `docs/diary/diary.js`: Declared state variables `bernieInstructionText` and `bernieInterpretResult`, implemented `renderBernieInstructionInput()`, integrated it with live pilot flows (`loadBernieLiveReview()`, `renderBernieReview()`, `renderBernieInterpretOnly()`, `initBernieReview()`), ensured `isConfirmAdapter` respects query parameters for smoke tests, added a check for `disabled` inside the `confirmBtn` click handler, and preserved `selected_candidate_index` and `reason` in `supervisedBody`.
  - `review/test_diary_smoke.py`: Added default route interceptor for `/appointments/proposals/bernie/interpret-booking-instruction`, added the `trigger_live_bernie` test helper, updated all live review tests to type instructions and click submit, updated confirm test assertions to avoid race conditions.
- Verification run:
  - Executed the full smoke test suite: `C:\Users\sarashera\emr4\.venv\Scripts\pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`
  - Result: All 46 tests PASSED successfully.
- Remaining risks:
  - None identified. The changes are fully gated within the Bernie pilot/live review mode (`isBerniePilotActive`). Normal mode operation remains unaffected and makes no automatic or manual interpretation/supervised booking calls.
