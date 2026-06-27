# antigravity-bernie-staff-visible-pilot-entry-path

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | superseded |
| Created | 225e821 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-bernie-staff-visible-pilot-entry-path --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-bernie-staff-visible-pilot-entry-path --commit-message "Bernie staff-visible pilot entry path" --message "antigravity-bernie-staff-visible-pilot-entry-path ready for Codex review"` |

## Mission

Plan, then after approval expose the existing supervised Bernie booking-assistant panel through a staff-visible non-default diary entry path for allowlisted pilot use.

## Scope

### In Scope

Plan packet first; after approval docs/diary UI assets and review harness updates as needed; visible entry only when the existing pilot/eligibility gate allows it; launcher must use real selected linked appointment context or another explicit non-manual context source; no manual patient/practitioner ID fields in staff-visible mode; dev/manual fallback may remain hidden behind explicit dev flags; preserve instruction readiness, compact context summary, supervised confirmation, no default production exposure, no autonomous writes, and asset version bumps if runtime assets change.

### Out of Scope

Backend/provider/schema/migration changes unless the plan proves a tiny contract-only adjustment is unavoidable; autonomous booking; default production exposure; query-string free-text intake; URL/browser-storage context persistence; PHI-heavy logging; patient/practitioner search redesign; taskpane; Command Centre; billing; SMS; resource admin; broad diary redesign; unrelated CSS cleanup.

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

Plan packet first; after approval bundled Node syntax check; route-intercepted checks proving default hidden/no-call, allowlisted visible launcher, selected linked appointment context flow, no manual ID exposure in staff-visible mode, instruction readiness/summary persistence, supervised confirmation gating, and confirm route intercepted; full diary review harness if diary runtime assets change; frontend version integrity; git diff --check.

## Merge Criteria

Codex accepts the plan before implementation; implementation stays within diary/review-harness boundary; staff-visible mode exposes only gated, explicit, supervised Bernie flow; no manual IDs or PHI persistence are introduced; deterministic checks pass; Pages asset versions are bumped and verified if runtime assets change.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: none by Antigravity. The Antigravity CLI exited with no stdout and left `antigravity/current` unchanged, so Ariadne/orchestrator implemented the sprint directly on `master`.
- Verification run: superseded before worker implementation.
- Remaining risks: none from the worker branch; Codex closeout owns the implemented verification evidence.
