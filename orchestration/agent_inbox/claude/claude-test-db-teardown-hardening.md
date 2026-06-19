# claude-test-db-teardown-hardening

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | queued |
| Created | cf47471 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-test-db-teardown-hardening --commit-message "Harden test DB teardown" --message "Test DB teardown hardening ready for Codex review"` |

## Mission

Fix the recurring test database teardown/reset instability that can leave the PostgreSQL test DB partially dropped, causing later pytest runs to fail with errors such as relation practices does not exist.

## Scope

### In Scope

Inspect tests/conftest.py and related test database setup/teardown code. Make teardown/reset more robust against lingering connections, lock contention, and rapid repeated test runs. Prefer a narrow fixture-level or helper-level fix. Add or update focused tests only if practical. Document exact verification commands and any residual risk in Completion Notes before submit.

### Out of Scope

Do not change production app behavior, migrations, diary frontend, taskpane, Command Centre, Gemini/AI code, or booking mutation logic. Do not move master or handoff/current. Do not mask real test failures by broadly ignoring database errors.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

.venv\Scripts\python.exe -m pytest tests\test_agent_worktrees.py -q is not relevant unless orchestration files are touched. Run the focused test suites that previously exposed the issue, at minimum .venv\Scripts\python.exe -m pytest tests\test_diary_roster.py tests\test_diary_template.py -q twice in succession if feasible. Run broader tests only if fixture changes risk shared test behavior. Report exact commands/results.

## Merge Criteria

Repeated focused pytest runs no longer leave the test DB in a partial state; the solution is scoped to test infrastructure; no production behavior changes are introduced; completion notes explain the fix and any remaining risk.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
