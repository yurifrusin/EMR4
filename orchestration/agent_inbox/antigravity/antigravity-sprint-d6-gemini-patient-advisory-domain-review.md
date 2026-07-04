# antigravity-sprint-d6-gemini-patient-advisory-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | eff7cdd |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-d6-gemini-patient-advisory-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-d6-gemini-patient-advisory-domain-review --commit-message "Sprint D6 Gemini patient advisory domain review" --message "antigravity-sprint-d6-gemini-patient-advisory-domain-review ready for Codex review"` |

## Mission

Use Antigravity/Gemini as an independent backend/domain-policy reviewer for D6 patient future-booking advisory semantics.

## Scope

### In Scope

Review build_patient_booking_context, has_existing_booking_on_requested_day, supervised booking warning generation, and tests. Produce a tangible review artifact with exact semantics for when existing_future_follow_up should be emitted versus when future bookings should remain informational context.

### Out of Scope

No UI/frontend. No GraphRAG. No persisted sessions/migrations. No broad rewrite. No staff-facing copy changes unless explicitly proposing future work.

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

If code changed: py_compile, focused pytest, git diff --check. If review-only: cite exact files/tests and submit artifact.

## Merge Criteria

Ariadne can use the review if it is concrete, file-grounded, and submitted as a repo artifact; stdout alone is not sufficient.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
