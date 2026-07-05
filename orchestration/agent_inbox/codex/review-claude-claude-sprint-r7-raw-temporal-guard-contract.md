# review-claude-claude-sprint-r7-raw-temporal-guard-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r7-raw-temporal-guard-contract` |
| Status | integrated |

## Review Request

claude-sprint-r7-raw-temporal-guard-contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - app/services/diary/temporal.py — added evaluate_raw_mutation_temporal_guard() pure helper + RawMutationTemporalKind Literal; updated __all__
  - app/routers/appointments.py — imported the helper; added temporal guard in _create_appointment_from_body (raises HTTP 422); added temporal guard in _apply_appointment_update (gated on date/time/duration keys, raises HTTP 422); added temporal block in _build_create_appointment_proposal (blocks list → safe=False, no signed evidence); added temporal block in propose_update_appointment (gated on date/time/duration incoming keys)
  - tests/test_appointment_raw_temporal_guard.py — new; 13 tests, all clock monkeypatching local per-test (no autouse fixture per Ariadne amendment)

- Verification run:
  - py_compile clean on all 3 files (python 3.14)
  - git diff --check: clean (no whitespace issues)
  - Pure-helper unit assertions (5 cases: past_date, window_fully_past, boundary, open-window, future) all passed without DB
  - Full integration test suite (pytest tests/test_appointment_raw_temporal_guard.py) could not run: no PostgreSQL running in claude/current worktree (port 5434 refused). Integration tests require a running DB. DB-level verification deferred to Codex integration environment.

- Remaining risks:
  1. Integration tests unverified locally (no DB in worktree). All 13 tests need Codex to run pytest against the integration DB.
  2. The create proposal builder now fires the temporal guard on every call (no "only when temporal fields in incoming" gate, because it is always a fresh create). This is correct but Codex should confirm the confirm_create_proposal route revalidates via _build_create_appointment_proposal, which will also re-gate — this is intentional and adds a defence-in-depth re-check at confirm time.
  3. Status/delete/waiting-area routes untouched per scope (they do not change appointment_date/start_time_local).

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-r7-raw-temporal-guard-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
