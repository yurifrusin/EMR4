# claude-sprint-n12-rich-schedule-explanation-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | superseded |
| Created | 1d18961 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-n12-rich-schedule-explanation-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-n12-rich-schedule-explanation-contract --commit-message "Dispatch Sprint N12 Claude rich explanation plan" --message "claude-sprint-n12-rich-schedule-explanation-contract ready for Codex review"` |

## Mission

Plan the backend/domain contract for rich roster and schedule explanation payloads in Bernie outcomes, so Bernie can explain practitioner-not-rostered, outside-hours, clinic-day-exhausted, and true searched-zero-slot situations in a friendly professional voice without letting explanation data grant confirmation authority.

## Scope

### In Scope

app/services/diary/outcomes.py; app/services/diary/reception_context.py; app/services/diary/schedule_explanations.py if present or a bounded new diary-domain helper; app/routers/appointments.py response adapter seams; focused backend tests for outcome payload semantics and confirm-affordance non-authority.

### Out of Scope

Persisted session database tables or migrations; GraphRAG route/UI wiring; auto-mode; broad root-to-branch API rewrite; taskpane/Command Centre changes; real PHI; letting retrieved/advisory facts set slot truth, hard policy, confirm affordance, freshness, audit evidence, or write payloads.

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

Plan first only. Later implementation should run focused Bernie outcome/supervised booking/schedule explanation tests, adjacent confirm gate/evidence tests, py_compile for touched Python, and git diff --check.

## Merge Criteria

Plan names typed payload fields, precedence rules, non-authority boundaries, tests, risks, and how Diary can render natural copy without inventing facts.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None by Claude. Claude headless returned the session-limit
  429 before producing a plan, so Ariadne superseded this lane.
- Verification run: Ariadne completed and verified the accepted N12 slice from
  Antigravity and Codex plans.
- Remaining risks: Retry Claude after quota refresh if a deeper backend/domain
  review is useful.
