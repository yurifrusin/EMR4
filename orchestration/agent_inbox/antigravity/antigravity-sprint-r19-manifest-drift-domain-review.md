# antigravity-sprint-r19-manifest-drift-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | da69414 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r19-manifest-drift-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r19-manifest-drift-domain-review --commit-message "Sprint R19 Manifest drift domain review" --message "antigravity-sprint-r19-manifest-drift-domain-review ready for Codex review"` |

## Mission

Gemini/Antigravity: review Sprint R19 drift guardrails from receptionist/product safety perspective. Focus on outcome copy and status-specific reason-code policy: what should be authoritative backend policy, what can remain display copy, and what wording risks matter before Bernie consumes the manifest.

## Scope

### In Scope

orchestration/bernie_diary_manifest_review.md, app/services/diary/capability_manifest.py, app/services/diary/outcomes.py, app/schemas/appointments.py, docs/diary/diary.js outcome/reason constants, orchestration review artifact.

### Out of Scope

Runtime prompt changes, codebase dumps into Gemini, database migrations, live AI calls, broad UI redesign, granting Bernie write authority.

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

Write a concise artifact under orchestration/ naming accepted drift guardrails, UX/domain risks, and recommended acceptance criteria for R19.

## Merge Criteria

Ariadne can use the artifact to decide which drift guards are safe to integrate before manifest prompt consumption.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/manifest_drift_review.md`.
- Verification run: static domain analysis of backend schemas, routes, outcome/schedule explanation code, and frontend `diary.js` constants; Ariadne integrated accepted policy points and deferred larger copy-source migration.
- Remaining risks: frontend schedule copy catalogs still duplicate backend schedule explanation wording and should be unified later.
