# codex-bernie-pilot-launch-context-guard

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-pilot-launch-context-guard` |
| Status | submitted |
| Created | 4c6d9b0 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-pilot-launch-context-guard --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-pilot-launch-context-guard --commit-message "Dispatch Sprint 61 Bernie pilot launch context guard" --message "Sprint 61 dispatched: Bernie pilot launch context guard"` |

## Mission

Harden the staff-visible Bernie pilot launch path so it does not rely on smoke/default practitioner or patient identifiers in ordinary mode. The pilot launch should fail closed or show a clear readiness message until real diary context is available.

## Scope

### In Scope

Diary frontend and deterministic review harness files only, plus coordination packets. Add narrow helpers/tests proving normal pilot launch does not POST supervised-booking with default smoke identifiers, eligible-but-context-missing state is labelled/read-only, smoke/dev/query review paths still work, and explicit approval remains required before confirm-Bernie.

### Out of Scope

No backend changes, no config/auth changes, no new live write path, no autonomous booking, no PHI, no provider/LLM calls, no taskpane/Command Centre/Office/resource admin/billing/SMS work.

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

node --check docs/diary/diary.js; python scripts/check_frontend_versions.py if assets change; pytest review/test_diary_smoke.py focused/full; git diff --check; prove no supervised-booking POST with default smoke identifiers in normal pilot mode and no confirm-Bernie POST before approval.

## Merge Criteria

Plan packet is submitted first and implementation only after Ariadne says complete sprint task; changes are scoped to pilot launch context/readiness; deterministic checks pass; no live writes or default smoke identifiers are used in ordinary staff-visible pilot mode.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-bernie-pilot-launch-context-guard.md` status/completion notes; `orchestration/agent_inbox/codex/plan-codex-codex-bernie-pilot-launch-context-guard.md` implementation plan packet.
- Verification run: Plan gate only; inspected packet/protocol and relevant Bernie diary/review harness surfaces. No production/test verification run because no implementation files were changed.
- Remaining risks: Implementation still needs Ariadne plan approval and explicit `complete sprint task`; ordinary pilot context may need to fail closed until a real selected practitioner/patient context is available.
