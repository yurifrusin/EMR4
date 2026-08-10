# Independent veto: behavior failure 044 bounded not-null telemetry

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r173`
- Branch: `codex/review-context-fabric-behavior-044-telemetry-d19de28f`
- Candidate: `d19de28f91fbdc05aeec96cabcb329ee7002a7f4`
- Immediate predecessor: `70545fd2012ec8f92ff9d89658e455e8ff3c5b07`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md; exact diff `70545fd2..d19de28f`; immutable attempt-044
failure and diagnosis; their scripts, tests and focused documents; the behavior
harness/evidence schema/tests; AER revisions 195-197, register, pattern report
and tests; and this packet, orchestrator receipt and worktree preflight. Inspect
the inert admission table only as needed to verify the closed column allowlist.
Do not inspect the mutable evidence alias, protected holdouts, historical Diary
data, `docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before/after, exact branch/diff and protected refs;
2. immutable failure-044 SHA-256 is
   `0bacbe855a818c4dbb6bfa5c95ffbdb4fd5a91ac9ace431153669d17cb277345`,
   attempt ID is `9e078edf28400c199b16b56b`, failure is BTR-I02
   `unexpected_rejection` / `23502`, cleanup is complete and no pass is claimed;
3. diagnosis proves the parent persisted only scenario/SQLSTATE, had a bounded
   bootstrap not-null parser but no scenario coordinate projection, and makes no
   claim about the actual null column or database-body defect;
4. candidate changes only bounded failure telemetry, deterministic diagnosis,
   AER and tests; database body, structural contract, DDL, behavior contract,
   fixtures, scenarios, parent hashes and runtime authority remain unchanged;
5. scenario coordinate parsing runs only for exact SQLSTATE `23502`, while every
   rejection retains its established safe SQLSTATE and optional function
   coordinate;
6. the allowlist contains exactly the one admission relation and its twenty
   typed columns; only its thirteen actual NOT NULL columns are diagnostic
   candidates, and hostile unlisted relations/columns fail closed;
7. durable evidence can receive only SQLSTATE, coordinate status, allowlisted
   relation/column and existing bounded fields; raw stdout/stderr never escapes;
8. exact envelope regressions cover non-23502 `CF303`, `42883` and `22P02`, plus
   allowlisted and hostile 23502 headers;
9. AER revision 197 contains exactly 231 closed incidents through AER-0231 and
   accurately records the assumed Docker path, missing coordinate and both
   precommit telemetry-envelope corrections;
10. the protected mutable alias is absent from clean r173 and no test depends on
    it;
11. all exact checks below pass with a clean postcondition; and
12. no Docker/PostgreSQL run, database-body fix, operational database,
    watcher/feed, application/API/Diary wiring, provider/product data,
    deployment, Pages or protected-ref boundary opens.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r173 tests\test_raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_044_not_null_coordinate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 70545fd2012ec8f92ff9d89658e455e8ff3c5b07..d19de28f91fbdc05aeec96cabcb329ee7002a7f4
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run the behavior harness,
contact another provider/product, inspect forbidden data, move refs or
self-accept. Return `revision_required` for any P0-P2 finding, drift, failed
check or dirty postcondition; otherwise return exact `pass`.
