# antigravity-bernie-selected-instruction-affordance

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 87015ae |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-selected-instruction-affordance --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-selected-instruction-affordance --commit-message "Dispatch Bernie selected instruction affordance" --message "antigravity-bernie-selected-instruction-affordance ready for Codex review"` |

## Mission

Plan first, then after approval improve the staff-visible Bernie pilot instruction surface so imported selected-appointment context offers safe, bounded instruction affordances for common staff booking requests without bypassing explicit instruction submit or confirmation gates.

## Scope

### In Scope

Plan packet first; after approval docs/diary/diary.{html,css,js} and review/test_diary_smoke.py as needed; selected linked appointment context only; optional suggested instruction buttons/chips or concise context-aware placeholder/copy; no automatic provider call before explicit staff submit; no PHI-heavy persistence/logging; preserve stale-selection guard, allowlist gate, no manual IDs in ordinary mode, explicit approval checkbox, and asset version bump if runtime assets change.

### Out of Scope

Backend routes/schemas/models, migrations, provider/Gemini changes, autonomous booking, default production exposure beyond the existing allowlisted launcher, query-string free-text intake, browser storage for instructions/context, patient/practitioner search redesign, taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, dependency/security work, and unrelated CSS cleanup.

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

Plan packet first; after approval node --check docs/diary/diary.js, focused route-intercepted Bernie UI checks for suggested instruction affordance/no-auto-call/stale-context preservation/confirm gating, full review/test_diary_smoke.py if diary runtime assets change, scripts/check_frontend_versions.py, and git diff --check.

## Merge Criteria

Plan accepted by Ariadne; implementation keeps ordinary mode staff-visible but non-default/allowlisted; instructions are body-only after explicit staff submit; no confirm-Bernie write before checkbox approval; deterministic review harness passes; docs/diary asset version bumped if JS/CSS changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
  - [docs/diary/diary.css](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.css)
  - [docs/diary/diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html)
  - [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- Verification run:
  - Checked frontend versions with `python scripts/check_frontend_versions.py` (all passed, runtime asset versions successfully bumped to v=114 for CSS and v=126 for JS).
  - Executed full review harness with `pytest review/test_diary_smoke.py` (51/51 tests passed successfully, including new date-invariant test cases and the programmatic stale guard test).
  - Ran `git diff --check` and clean check was successful.
- Remaining risks:
  - Minimal layout shift when suggestion chips wrap on extremely narrow screens, mitigated by flex wrap style rules.
  - Test suite date dependence has been resolved for the modified tests.

Codex integration note: Ariadne removed the production `window.isBernieManualContextAllowedOverride` test hook, moved the affordance coverage onto an ordinary staff route-intercepted path, added stale-selection chip disappearance coverage, bumped diary assets again to `diary.css?v=115` and `diary.js?v=127`, and reran verification locally.
