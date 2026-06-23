# plan-codex-codex-dev-data-duplicate-audit-tool

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-dev-data-duplicate-audit-tool` |
| Status | pending_plan_review |
| Created | 2026-06-23 10:11 +1000 |
| Source HEAD | `0456387` |

## Plan Summary

Add read-only dev duplicate audit helper

## My Understanding

Build a developer-only, read-only helper so Yuri can inspect likely duplicate patient rows and understand what each candidate is linked to before any human considers merge/delete work. The helper should replace the current ad hoc SQL in the dummy's guide with a safer command path and plain-English output. It must not change runtime app behaviour.

## Intended Surface / Boundary

Surface affected: command-line developer tooling under scripts/ plus the dev environment dummy's guide. Nearby surfaces that must not change: taskpane patient search UI, diary grid, waiting room panels, booking slots, appointment status controls, Command Centre, backend patient create/update validation, migrations, and any production admin UI/API. No clinical data mutation.

## Out Of Scope

No automatic deletion, no patient merge, no FK rewrites, no app route/schema changes unless a later approval explicitly expands scope, no production-facing duplicate admin workflow, and no changes to duplicate-blocking behaviour in patient create/update.

## Files I Expect To Edit

scripts/audit_patient_duplicates.py as the new read-only helper. docs/emr4-development-environment-dummys-guide.md to replace or point away from manual duplicate SQL. Possibly tests/test_audit_patient_duplicates.py if a focused smoke/unit test is practical without over-coupling to the local dev database.

## Implementation Steps

1. Add an argparse CLI helper that imports the existing SQLAlchemy settings/session and refuses to perform anything except reads.
2. Query likely duplicate groups by normalized same first name + last name + DOB, duplicate Medicare number + IRN, and duplicate IHI, ignoring blank/null identifiers.
3. For each patient in duplicate groups, print identity details plus reference counts from tables with FKs to patients.id; prefer SQLAlchemy metadata/reflection where safe so new patient-linked tables are not silently missed.
4. Keep output readable by default: grouped headings, patient IDs, created/updated dates, contact identifiers, document URL presence, and per-table counts. Consider optional --patient-id/--practice-id/--json only if they stay small and read-only.
5. Fail safely when database settings/connection are unavailable: clear error message, non-zero exit, no stack dump by default.
6. Update the dummy's guide to recommend the helper first and keep any raw SQL framed as fallback/read-only only.
7. Run verification after approval: helper against dev DB if available, safe-failure check with an invalid DB URL or missing settings path, syntax/compile check, and any focused tests added.

## Visual / Behavioural Acceptance Checks

The helper output should be understandable to a non-database expert: duplicate group, patient record, linked references, and table/count labels should be explicit. It should show enough information to choose what to inspect next, without implying deletion is safe. No UI visuals, cards, panels, diary grid, waiting room, booking slot, stacking, or status display is affected.

## Risks / Ambiguities

The exact reference counts universe may grow as models are added; metadata/reflection should reduce that risk, but imported models must be complete. Some historical/generated files may not be represented in DB references, so docs should warn that file cleanup is a separate manual check. Dev DB availability may vary, so verification may include a safe-failure path if the database is not running.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
