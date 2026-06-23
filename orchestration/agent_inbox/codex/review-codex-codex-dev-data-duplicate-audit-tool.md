# review-codex-codex-dev-data-duplicate-audit-tool

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-dev-data-duplicate-audit-tool` |
| Status | queued |

## Review Request

Dev data duplicate audit helper ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `scripts/audit_patient_duplicates.py` - read-only duplicate patient audit helper with same-name+DOB, Medicare+IRN, IHI grouping, per-patient FK reference counts, human output, JSON output, and safe error handling.
  - `docs/emr4-development-environment-dummys-guide.md` - duplicate inspection guidance now points to the helper first and warns against manual delete/update/FK rewrites.
  - `tests/test_audit_patient_duplicates.py` - focused grouping tests for duplicate identifiers and practice scoping.
  - `orchestration/agent_inbox/codex/plan-codex-codex-dev-data-duplicate-audit-tool.md` - captured approved implementation plan.
- Verification run:
  - `python -m py_compile scripts\audit_patient_duplicates.py tests\test_audit_patient_duplicates.py` - passed.
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_audit_patient_duplicates.py -q` - passed, 2 tests. Pytest emitted the existing `pytest_asyncio` loop-scope deprecation warning.
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe scripts\audit_patient_duplicates.py` - passed against dev DB; found 1 likely duplicate group for Billy Frusin and printed appointment reference counts for both records.
  - Invalid DB URL safe-failure check with `DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:1/gp_pms_dev` - exited 2 with a plain error and `No records were changed.`
  - Missing-dependency safe-failure check with system `python scripts\audit_patient_duplicates.py` - exited 2 with `No module named 'sqlalchemy'` and `No records were changed.`
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe scripts\audit_patient_duplicates.py --json | C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m json.tool > $null` - passed.
  - `git diff --check` - passed; Git printed a CRLF normalization warning for this task packet only.
- Remaining risks:
  - Reference counts cover database tables with foreign keys to `patients.id`; generated patient files or other non-DB artefacts still need separate manual review before any future merge/delete work.
  - The durable Codex mirror has no local `.venv`, so DB-path verification used the shared project virtualenv at `C:\Users\YuriFrusin\Documents\EMR4\.venv`.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-dev-data-duplicate-audit-tool.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
