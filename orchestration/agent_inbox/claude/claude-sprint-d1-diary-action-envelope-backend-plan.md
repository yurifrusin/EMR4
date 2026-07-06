# claude-sprint-d1-diary-action-envelope-backend-plan

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 7bab79b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint-d1-diary-action-envelope-backend-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint-d1-diary-action-envelope-backend-plan --commit-message "Sprint D1 diary action envelope backend plan" --message "claude-sprint-d1-diary-action-envelope-backend-plan ready for Codex review"` |

## Mission

Review the post-G1-G6 signed-confirm spine and plan the first bounded backend extraction toward a native Diary action envelope module. Focus on create/update/status/delete confirm routes and how Bernie/human callers should share typed action contracts without broad API rewrite.

## Scope

### In Scope

app/routers/appointments.py, app/schemas/appointments.py, app/services/diary/*, app/services/bernie/evidence.py, tests around appointment proposals/status/delete/audit, orchestration docs

### Out of Scope

No persisted PHI session table, no GraphRAG, no auto-mode, no broad root-to-branch API review, no raw endpoint removal unless explicitly justified as safe and tiny, no frontend redesign

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

Plan should name exact files to change, invariants to preserve, focused tests, and migration/compatibility risks. Do not implement production code during plan phase.

## Merge Criteria

Ariadne can approve a small D1 implementation that reduces route-local string/contract sprawl, preserves all G1-G6 behaviours, and makes next Bernie native diary actions easier.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan phase only — no production code edited. Wrote the implementation-plan packet
  `orchestration/agent_inbox/codex/plan-claude-claude-sprint-d1-diary-action-envelope-backend-plan.md`
  and moved this source packet to `pending_plan_review`. The plan proposes (for the approved
  implementation phase): new `app/services/diary/confirm_actions.py`, edits to
  `app/routers/appointments.py`, `app/services/diary/__init__.py`, optional
  `app/services/diary/capabilities.py`, and a new focused `tests/` regression test.
- Verification run: Plan phase — no code executed. Read-only inspection of `app/routers/appointments.py`
  (5 confirm routes + verify pipelines), `app/schemas/appointments.py` (confirm In/Out schemas),
  `app/services/diary/*` (envelopes, confirm_gate, capabilities), and
  `app/services/bernie/evidence.py` / `bernie_turn_evidence.py` (5 signed-evidence purpose constants).
  Confirmed the diary envelope/capability contracts exist but are not yet wired to the confirm routes.
- Remaining risks: Silent contract drift (mitigated by a regression test pinning exact pre-D1 endpoint
  literals + evidence purposes); diff-size vs sprawl tension (mitigated by thin per-action wrappers
  delegating to a shared factory); generic block-response factory must accept the differing
  `Confirm*ProposalOut` output types; new capabilities.py↔router path invariant. Open question for
  Codex: fold the five verify pipelines into one shared function now, or defer to D2? Plan recommends
  defer.
