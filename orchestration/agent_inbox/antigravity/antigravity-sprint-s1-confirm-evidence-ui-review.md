# antigravity-sprint-s1-confirm-evidence-ui-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | accepted |
| Created | 11cbb2c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-s1-confirm-evidence-ui-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-s1-confirm-evidence-ui-review --commit-message "Sprint S1 confirm evidence UI review" --message "antigravity-sprint-s1-confirm-evidence-ui-review ready for Codex review"` |

## Mission

Plan Sprint S1 Diary UI work for carrying backend signed evidence through candidate selection, auto-preview, stale-state clearing, and confirm affordance rendering without making the UI the authority.

## Scope

### In Scope

Plan only first. docs/diary/diary.js evidence echo paths, review/test_diary_smoke.py stale/confirm fixtures, asset-version/check strategy if later UI code changes are approved. Identify how UI should treat missing/malformed evidence and how to preserve composer/session stale clearing.

### Out of Scope

No implementation before plan gate, no backend route/schema changes, no visual redesign, no GraphRAG/practice knowledge UI wiring, no auto-confirm/auto-mode, no booking modal rewrite outside evidence echo if later approved.

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

Plan packet first. Later UI implementation should run node --check, scripts/check_frontend_versions.py, focused diary smoke tests for signed evidence echo/stale confirm suppression, and git diff --check.

## Merge Criteria

Concrete plan showing the UI merely echoes server evidence and renders backend confirm_affordance decisions, with no client-side authority over freshness or confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes
 
Required before submit. These notes are copied into Codex's review packet automatically:
 
- Files changed:
  - [plan-antigravity-antigravity-sprint-s1-confirm-evidence-ui-review.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint-s1-confirm-evidence-ui-review.md)
  - [antigravity-sprint-s1-confirm-evidence-ui-review.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/agent_inbox/antigravity/antigravity-sprint-s1-confirm-evidence-ui-review.md)
- Verification run:
  - Plan initialized and drafted; no production code changes made (plan gate).
- Remaining risks:
  - Enforcing strict fail-closed behavior on client-side rendering when `confirm_affordance` is missing or invalid.
