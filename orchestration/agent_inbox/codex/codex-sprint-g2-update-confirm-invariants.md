# codex-sprint-g2-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 37ed8b2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-g2-update-confirm-invariants --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-g2-update-confirm-invariants --commit-message "Sprint G2 update confirm invariants" --message "codex-sprint-g2-update-confirm-invariants ready for Codex review"` |

## Mission

Plan adversarial invariants for migrating human Diary update writes to the G1 signed update-confirm route: replay, stale state, cross-appointment/cross-practice, warning acceptance, audit, and no raw-PUT bypass through confirm UI.

## Scope

### In Scope

tests around appointment update confirm evidence, human UI confirm payload use, stale/conflict/no-mutation properties, audit codes, and raw PUT compatibility boundary documentation.

### Out of Scope

Production code during plan gate; broad action grammar; status/cancel/delete; persisted session tables; GraphRAG; UI redesign.

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

Focused pytest targets for update confirm and existing update proposal tests; review smoke assertions if UI changes; diff check.

## Merge Criteria

Plan is implementation-ready, adversarial, scoped, and explicitly distinguishes backend compatibility PUT from evidence-gated UI confirm authority.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/codex-sprint-g2-update-confirm-invariants.md`
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g2-update-confirm-invariants.md`
- Verification run:
  - Planning mode only; read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and `orchestration/agent_inbox/codex/codex-sprint-g2-update-confirm-invariants.md`.
  - Ran required `handin --agent codex` with explicit venv Python path from `C:\Users\sarashera\EMR4-worktrees\codex`; succeeded and reported already up to date at `85166f0`.
  - Ran required `plan --agent codex --task codex-sprint-g2-update-confirm-invariants ...`; succeeded and wrote the implementation-plan packet.
  - Focus-read G1 update-confirm backend route/schema/tests and Diary human edit/drag/resize raw-PUT call sites.
  - No production code or tests were edited or run.
- Remaining risks:
  - Later implementation must decide whether to neutralize the Bernie-named update-confirm schema or keep a compatible alias while avoiding G1 regressions.
  - Diary edit modal currently combines appointment update with a separate status PATCH; G2 must not accidentally fold status semantics into the update-confirm route.
  - Raw PUT should remain a bounded authenticated staff/API compatibility path, but the migrated Diary confirm UI must not use it as confirmation authority.
