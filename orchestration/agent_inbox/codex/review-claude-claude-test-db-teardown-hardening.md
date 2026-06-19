# review-claude-claude-test-db-teardown-hardening

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-test-db-teardown-hardening` |
| Status | integrated |

## Review Request

Test DB teardown hardening ready for Codex review

## Worker Completion Notes

- **Files changed:** `tests/conftest.py` only — no production code touched.

- **Root cause:** The session-scoped `engine` fixture used SQLAlchemy's default connection pool. After a test session's `drop_all` teardown, pooled connections from the previous session remained open in PostgreSQL, holding `AccessShareLock` on tables. The next session's `TRUNCATE practices RESTART IDENTITY CASCADE` in `clean_db` would deadlock against those locks. On rapid successive runs the partial-drop state left `relation "practices" does not exist` errors.

- **Fix:**
  1. `NullPool` on the test engine (`create_engine(TEST_DB_URL, poolclass=NullPool)`). Every connection is closed at the TCP socket level the moment it's returned, so no connections linger between tests or between runs. This is the primary fix.
  2. Retry loop (3 attempts, 0.5 s delay) around `TRUNCATE` in `clean_db` as defence-in-depth. The retry is silent on first/second failure and re-raises on third; it does not mask real test assertion failures.
  3. Removed the earlier intermediate attempt that used `pg_terminate_backend` — unnecessary with NullPool and it introduced its own timing hazard (terminated backends mid-rollback still hold locks briefly).

- **Verification run:**
  ```
  cd C:\Users\YuriFrusin\Documents\EMR4-worktrees\claude
  # Run 1:
  python -m pytest tests/test_diary_roster.py tests/test_diary_template.py -q
  # → 18 passed in 55.79s
  # Run 2 (immediately after):
  python -m pytest tests/test_diary_roster.py tests/test_diary_template.py -q
  # → 18 passed in 36.52s
  # No errors, no partial-DB state between runs.
  ```

- **Remaining risks:** NullPool creates a new TCP connection per `engine.connect()` call, so test suite wall-clock time increases slightly (~10–20 % for short tests). For this suite (multi-second DB round trips per test) the overhead is negligible. If a future test does many small queries in a tight loop, `StaticPool` or a short-lived pool would be a better fit — but that is not the case today.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-test-db-teardown-hardening.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. The fix is scoped to `tests/conftest.py`;
  Codex reran the focused diary roster/template tests twice after integration and
  both runs passed without the prior partial-DB failure.
- Follow-up required: Address the unrelated `pytest_asyncio` loop-scope
  deprecation warning later.
