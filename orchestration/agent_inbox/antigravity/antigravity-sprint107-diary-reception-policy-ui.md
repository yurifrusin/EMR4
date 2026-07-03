# antigravity-sprint107-diary-reception-policy-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | pending_plan_review |
| Created | 0beddab |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint107-diary-reception-policy-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint107-diary-reception-policy-ui --commit-message "sprint107 diary reception policy ui" --message "antigravity-sprint107-diary-reception-policy-ui ready for Codex review"` |

## Mission

Plan-gated Sprint 107 UI lane: make the Diary Bernie panel consume backend reception_policy/reception_context fields so logically wrong messages cannot render. Use typed availability/reason-code facts rather than brittle text checks.

## Scope

### In Scope

docs/diary/diary.js, docs/diary/diary.css only if needed, review/test_diary_smoke.py or existing diary review harness updates, diary asset version bump if runtime assets change, orchestration packet status/plan artifacts

### Out of Scope

Backend API/schema changes, database migrations, broad state-machine rewrite, persisted sessions, limited Bernie auto-mode, patient-specific copy branches, changing booking/confirmation behavior

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

Submit a plan first. Proposed implementation verification should include node --check docs/diary/diary.js, scripts/check_frontend_versions.py if assets change, and focused review/pytest assertions proving: no matching-times copy appears only when reception_policy.search_ran_no_candidates is true; roster_unavailable renders as roster/schedule unavailable; advisory future bookings do not block candidate display; stale latest/history behavior is not regressed.

## Merge Criteria

Plan must preserve old response compatibility, consume reception_policy when present with safe fallback for older responses, avoid brittle message-string branching, and leave confirmation/booking mutation paths unchanged.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: C:\Users\sarashera\EMR4-worktrees\antigravity\orchestration\agent_inbox\codex\plan-antigravity-antigravity-sprint107-diary-reception-policy-ui.md, C:\Users\sarashera\EMR4-worktrees\antigravity\orchestration\agent_inbox\antigravity\antigravity-sprint107-diary-reception-policy-ui.md
- Verification run: Pytest smoke test run completed successfully on baseline branch; no production changes made yet.
- Remaining risks: Backward compatibility of legacy API responses (which lack reception_policy) when parsing them in diary.js. This is addressed in the plan via defensive checks.
