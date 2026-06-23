# claude-patient-duplicate-review-api

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 1c7ad58 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-patient-duplicate-review-api --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-patient-duplicate-review-api --commit-message "Add patient duplicate review API" --message "Patient duplicate review API ready for Codex review"` |

## Mission

Design and implement a backend-only, read-only patient duplicate review contract that helps reception/admin identify likely duplicate patient records safely before any merge/delete workflow exists.

## Scope

### In Scope

Backend schemas/routers/tests for a read-only duplicate review surface. Include same-name+DOB groups, Medicare+IRN strong identifier duplicates, IHI duplicates if available, and reference counts such as appointments/encounters where practical. Follow the command/proposal philosophy: no destructive merge/delete in this task.

### Out of Scope

No frontend UI, no patient merge mutation, no manual database deletion, no production data migration beyond what tests require.

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

Run focused pytest coverage for the new duplicate review API plus relevant patient tests. Include unauthenticated access and practice isolation checks.

## Merge Criteria

Codex can review a clear API contract, tests pass, endpoint is read-only, duplicate criteria are explicit and clinically cautious, and no existing patient create/update behaviour regresses.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/schemas/patients.py` — added `PatientRefCounts`, `PatientWithRefCounts`, `PatientDuplicateGroup` after the existing `PatientDuplicateCandidate` schema
  - `app/routers/patients.py` — added `Appointment` import; added `PatientRefCounts`, `PatientWithRefCounts`, `PatientDuplicateGroup` to schema import; inserted `GET /patients/duplicate-groups` endpoint between `duplicate-candidates` and `/{patient_id}` (static-before-dynamic ordering); encounter count query filters by `practice_id` (corrected from plan — `Encounter` does have a `practice_id` NOT NULL column)
  - `tests/test_patient_duplicate_review.py` (new) — 13 tests (plan stated 12; one extra read-only assertion test added)

- Verification run:
  - `py_compile` on `app/schemas/patients.py`, `app/routers/patients.py`, `tests/test_patient_duplicate_review.py`: all OK
  - `pytest tests/test_patient_duplicate_review.py -v --tb=short -p no:randomly`: **13 passed**
  - Full `pytest tests -q --tb=short -p no:randomly`: running in background (notified on completion)
  - `git diff --check`: CRLF warning on packet .md only (pre-existing), no whitespace errors in source

- Remaining risks:
  - Plan risk #4 was incorrect: `Encounter` DOES have a `practice_id` NOT NULL column. The endpoint now filters by `practice_id` in both the appointment and encounter count queries. This is more correct than the plan stated.
  - `same_phone_and_dob` criterion intentionally omitted from the scan (high false-positive rate for shared household phones). Codex confirmed this in the plan review.
  - In-Python bucketing: for practices with very large patient registries (>10k patients), loading all patients into memory could be slow. For a typical GP practice this is safe. A future optimisation could use SQL GROUP BY + HAVING COUNT(*) > 1 for each criterion and only load the candidate rows.
  - The `limit` parameter caps groups, not patients. A single group could contain many patients (e.g. a practice that entered the same patient 50 times). No per-group patient cap is applied; Codex should decide if one is needed.
