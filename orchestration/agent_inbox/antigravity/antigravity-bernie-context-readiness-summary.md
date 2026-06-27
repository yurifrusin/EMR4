# antigravity-bernie-context-readiness-summary

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 2358559 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-context-readiness-summary --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-context-readiness-summary --commit-message "Dispatch Bernie context readiness summary sprint" --message "Plan for Bernie context readiness summary"` |

## Mission

Plan first, then after approval improve the existing Bernie pilot panel so the staff instruction input is only presented as actionable after valid practitioner/patient context is ready, and a compact selected-context summary remains visible through instruction and confirmation states.

## Scope

### In Scope

Plan packet first; after approval docs/diary/diary.js, docs/diary/diary.css, docs/diary/diary.html if runtime assets need version bumps, and review/test_diary_smoke.py. Add/adjust UI state so no-context/manual-context-blocked state does not present an actionable instruction submit. After staff imports a linked selected appointment or submits valid manual context, show a compact non-PHI context summary in the Bernie review panel through instruction and confirmation states, e.g. selected appointment patient name/time and practitioner label where available, while preserving manual fallback. Preserve explicit selected-context import, explicit instruction submit, explicit approval checkbox/button gate, and in-memory-only context.

### Out of Scope

Backend routes, schemas, models, migrations, provider behavior, appointment mutation semantics, patient/practitioner search, production/default exposure changes, autonomous booking, taskpane, Command Centre, billing, SMS, resource admin, broad redesign, PHI-heavy logging, URL/query/localStorage/sessionStorage/cookie persistence for context or instruction, and unrelated CSS cleanup.

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

Plan packet first. After approval run bundled Node syntax check for docs/diary/diary.js, focused route-intercepted Playwright/pytest checks proving instruction submit is not actionable before context, selected appointment summary persists after import and on confirmation, existing explicit gates remain, full review/test_diary_smoke.py if diary runtime assets change, scripts/check_frontend_versions.py, and git diff --check.

## Merge Criteria

Codex can merge when the plan is accepted, implementation remains within the Bernie pilot panel readiness/summary surface, no safety gates or persistence boundaries are weakened, verification passes, and any changed runtime diary assets have cache-busted versions.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
