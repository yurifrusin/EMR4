# claude-python-security-baseline

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | 72396f8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-python-security-baseline --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-python-security-baseline --commit-message "Python Security Baseline" --message "claude-python-security-baseline ready for Codex review"` |

## Mission

Plan and implement a small Python/backend security baseline for EMR4: fast dependency and static-analysis checks that can run locally and in GitHub Actions without requiring secrets.

## Scope

### In Scope

Plan-gated. Likely files: .github/workflows/python-security.yml or equivalent, requirements/security tool notes if needed, minimal docs for exact commands. Consider pip-audit and Bandit for app/ while avoiding noisy/generated paths. Keep checks deterministic and Windows/GitHub Actions friendly. Also research Claude Code's currently available plugins/skills/tools for security and developer feedback loops, and include any concrete recommendations or "not worth it yet" findings in the plan/completion notes.

### Out of Scope

Do not change production app behavior, migrations, diary UI, taskpane/Command Centre, seed data, patient files, authentication semantics, or runtime dependencies unless the plan justifies a tiny dev-only tooling dependency. Do not handle Node/Office npm audit; Antigravity owns that lane. Do not move master or handoff/current.

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

Before submit, run the new local Python security commands if feasible, plus .venv\Scripts\python.exe -m py_compile over any changed Python helper files. If adding GitHub Actions only, validate YAML shape and document any commands that require network. Report exact command output.

## Merge Criteria

Ariadne can run or clearly understand the Python security checks; failures are actionable rather than noisy; no production behavior changes; workflow/docs are scoped and do not require secrets.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
