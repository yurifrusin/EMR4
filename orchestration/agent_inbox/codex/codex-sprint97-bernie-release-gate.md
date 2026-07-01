# codex-sprint97-bernie-release-gate

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/sprint97-bernie-release-gate` |
| Status | completed |
| Created | 89fb530 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint97-bernie-release-gate --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint97-bernie-release-gate --commit-message "Sprint 97 Bernie release-gate and review harness repair" --message "codex-sprint97-bernie-release-gate ready for Codex review"` |

## Mission

Independently plan the review-process repair that prevents Sprint 96's false pass: the simplest live Bernie booking prompt must be a hard gate, not a post-closeout suggestion.

## Scope

### In Scope

Plan packet first only. Read review/test_diary_smoke.py, scripts/smoke_bernie_interpreter.py, orchestration/sprint_closeout.md Sprint 96 section, orchestration/protocol_alerts.md, and relevant Bernie tests. Propose exact changes to test names, review harness, closeout protocol, and any new local/live smoke script or pytest marker needed to distinguish fixture, deterministic, and true provider-backed checks.

### Out of Scope

Production backend/frontend implementation before plan approval; broad orchestration rewrite; live GCP console actions; provider credential changes; unrelated diary/taskpane work; weakening confirmation/audit/RBAC gates.

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

Plan must include at least one deterministic automated gate for the Margaret Thompson/Dr Shera ordinary prompt, one explicit live-provider readiness gate or skip-with-fail policy, and closeout wording changes that make residual user tests blocking when they are basic happy paths.

## Merge Criteria

Ariadne can approve only if the plan makes it structurally hard to call route-intercepted tests 'live', and if Sprint 97 cannot close while the screenshot failure remains reproducible.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- `orchestration/bernie_release_gates.md`
- `orchestration/protocol_alerts.md`
- `orchestration/sprint_closeout.md`
- `orchestration/agent_inbox/codex/codex-sprint97-bernie-release-gate.md`
- Verification run: `git diff --check`; `Select-String -Path orchestration\bernie_release_gates.md,orchestration\protocol_alerts.md,orchestration\sprint_closeout.md -Pattern "route-intercepted|live_provider|screenshot|Margaret Thompson|Dr Shera"`.
- Remaining risks: This worker deliberately did not edit the owned implementation surfaces (`app/`, `docs/diary/`, `review/test_diary_smoke.py`, `scripts/smoke_bernie_interpreter.py`). Claude/Antigravity/Ariadne still need to implement the actual automated gates and resolve the reproducible screenshot failure before Sprint 97 can close.
