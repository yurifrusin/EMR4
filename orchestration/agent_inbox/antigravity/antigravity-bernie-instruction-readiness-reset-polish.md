# antigravity-bernie-instruction-readiness-reset-polish

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 6cd6a25 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-instruction-readiness-reset-polish --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-instruction-readiness-reset-polish --commit-message "Dispatch Bernie instruction readiness polish" --message "antigravity-bernie-instruction-readiness-reset-polish ready for Codex review"` |

## Mission

Plan first, then after Codex approval refine the staff-visible Bernie selected-appointment instruction surface so chip-filled instructions communicate ready-to-submit state without implying booking, and reset cleanly when context is changed, re-imported, or made stale.

## Scope

### In Scope

Plan packet first; after approval docs/diary/diary.{html,css,js} and review/test_diary_smoke.py as needed; selected linked appointment context only; clear readiness/status copy after chip selection or typed instruction; reset instruction/interpreter state when Change is clicked, current appointment is re-imported, or imported context becomes stale; no automatic provider call before explicit staff submit; preserve stale-selection guard, allowlist gate, no manual IDs in ordinary mode, no URL/browser-storage instruction persistence, explicit approval checkbox, and asset version bump if runtime assets change.

### Out of Scope

Backend routes/schemas/models, migrations, provider/Gemini changes, autonomous booking, default production exposure changes, query-string free-text intake, browser storage for instructions/context, patient/practitioner search redesign, taskpane, Command Centre, billing, SMS, resource admin, broad diary redesign, dependency/security work, and unrelated CSS cleanup.

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

Plan packet first; after approval bundled Node syntax check for docs/diary/diary.js, focused route-intercepted Bernie UI checks for chip/typed readiness copy, Change reset, re-import reset, stale-context reset/no chips/no call, confirmation gating, full review/test_diary_smoke.py if diary runtime assets change, scripts/check_frontend_versions.py, and git diff --check.

## Merge Criteria

Plan accepted by Ariadne; implementation keeps ordinary mode staff-visible but non-default/allowlisted; readiness copy is staff-supervised and does not imply booking; chip/typed instruction remains body-only after explicit staff submit; context changes clear pending instruction/interpret state; no confirm-Bernie write before checkbox approval; deterministic review harness passes; docs/diary asset versions bumped if JS/CSS changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
