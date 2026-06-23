# codex-dev-data-duplicate-audit-tool

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | integrated |
| Created | 1c7ad58 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-dev-data-duplicate-audit-tool --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-dev-data-duplicate-audit-tool --commit-message "Add dev patient duplicate audit helper" --message "Dev data duplicate audit helper ready for Codex review"` |

## Mission

Create a safe developer-only helper for inspecting duplicate patient records and their references, so Yuri can diagnose duplicates without needing ad hoc SQL or risky manual deletion.

## Scope

### In Scope

A script or documented command path under scripts/ that lists likely duplicate patients, duplicate Medicare+IRN/IHI groups, and per-patient reference counts. It must default to read-only output. Update the dummy's guide to point to the helper if implemented.

### Out of Scope

No automatic deletion, no patient merge mutation, no production admin UI, no changes to patient create/update validation unless needed for the read-only helper.

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

Run the helper against the dev database if available, run any added unit/smoke checks, and confirm it fails safely if DB settings are unavailable.

## Merge Criteria

Tool is read-only by default, output is understandable to a non-database expert, docs explain how to use it, and no app runtime behaviour is changed.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
