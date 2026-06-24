# claude-backend-dev-loop-tooling

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | bd13038 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-backend-dev-loop-tooling --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-backend-dev-loop-tooling --commit-message "Dispatch Sprint 22 backend dev tooling" --message "claude-backend-dev-loop-tooling ready for Codex review"` |

## Mission

Plan, then after approval improve EMR4 backend development feedback loops so Ariadne and worker agents can run fast, reliable checks before asking Yuri for residual manual review.

## Scope

### In Scope

Backend/dev-environment tooling only: pytest command ergonomics, Python static checks, run_dev/startup verification, documentation of backend check tiers, and small scripts or config that reduce false starts. May touch app config only for developer-environment safety, scripts, tests tooling, pyproject/requirements docs, and orchestration notes if needed.

### Out of Scope

Product behaviour, clinical routes unless only import/startup safety is affected, diary/taskpane UI, migrations, database schema, WhatsApp production send behaviour, security alert dismissal, and broad dependency upgrades not justified by the plan.

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

Plan packet first. After approval: app import/startup check, targeted pytest/static-check commands proposed in the plan, run_dev or equivalent non-destructive probe where feasible, git diff --check, and exact command outputs in Completion Notes.

## Merge Criteria

Ariadne can run a documented fast backend check tier and a broader confidence tier; changes do not make local startup more brittle; no secrets or PHI appear in logs/docs; existing backend tests are not weakened.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
