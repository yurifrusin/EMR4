# review-claude-claude-diary-roster-dev-data-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-diary-roster-dev-data-contract` |
| Status | queued |

## Review Request

Diary roster dev-data contract ready for Codex review

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-diary-roster-dev-data-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes (from claude)

**Files changed:**
- `seed.py` — added idempotent `Room` (Room 1/2/3) and `DiaryRoster` seeding for today, mirroring the 3 diary template columns: Room 1 → Dr Shera (practitioner_id + AHPRA), Room 2 → label "Nurse", Room 3 → label "[Available]". Imports `Room`, `DiaryRoster` from `app.models.diary`.
- `tests/test_diary_roster.py` — added `test_roster_requires_date_param` (missing `date` param → 422) and `test_roster_mixed_assigned_and_unassigned` (rooms with and without roster entries in same response). Total: 11 roster tests.
- `orchestration/agent_inbox/codex/review-claude-claude-diary-roster-dev-data-contract.md` — this file (review packet written by submit, completion notes added separately).

**Verification:**
```
cd C:\Users\YuriFrusin\Documents\EMR4-worktrees\claude
python -m pytest tests/test_diary_roster.py tests/test_diary_template.py -v
# Result: 18 passed in 79.28s (on a clean test DB)
```

**Remaining risk — test DB teardown deadlock:**
The session-scoped `engine` fixture in `tests/conftest.py` calls `Base.metadata.drop_all(eng)` on teardown. Under rapid successive test runs this occasionally deadlocks on `DROP TABLE reminders`, leaving the test DB in a partial state. The next invocation then fails with `relation "practices" does not exist` (tables partially dropped, `create_all` is a no-op for survivors). The fix used in this session was:
```python
from sqlalchemy import create_engine, text
eng = create_engine('postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_test')
with eng.connect() as conn:
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector')); conn.commit()
from app.models.base import Base; import app.models
Base.metadata.drop_all(eng); Base.metadata.create_all(eng)
eng.dispose()
```
This is a pre-existing infra issue — not introduced by this task. Suggested follow-up: add retry/`LOCK TABLE` logic to the `engine` teardown, or wrap `drop_all` in a `try/except` that logs and continues.

- Review result:
- Follow-up required:
