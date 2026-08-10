# Independent veto: behavior attempt 043 missing-source SQLSTATE correction

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r172`
- Branch: `codex/review-context-fabric-behavior-043-correction-77afc481`
- Candidate: `77afc48114328061c6cd3deef12b46fdf2a51ae6`
- Immediate predecessor: `656da9851f113c7ab639fc7634307c7be4a32cd6`
- Accepted parse baseline: `662fcae68308061faf09f4b3a8820baeaa417d88`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md; exact diff `656da985..77afc481`; immutable attempt-043
failure and diagnosis evidence; their scripts, tests and two focused documents;
the behavior plan/design/contract/harness/evidence schema/tests; the accepted
typed-body and inert-renderer paths needed to trace exact-row cardinality;
AER revision 194, register, pattern report and tests; and this packet,
orchestrator receipt and worktree preflight. Do not inspect the mutable evidence
alias, protected holdouts, historical Diary data, `docs/branding/`,
patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before and after, exact branch, exact diff and protected
   refs;
2. immutable attempt-043 failure SHA-256 is
   `00805d8b31ba445523a9a3e82581e07a4232873164ba49961ae5913f15617801`,
   attempt ID is `ab47183c26c84f1d61209e49`, failure is
   `scenario/sqlstate_mismatch`, cleanup is complete and no pass is claimed;
3. diagnosis evidence SHA-256 is
   `b30b84c9b1724fb4ac6a7bbb2c472c6ae23d572a9d9718b7a2459c0fbb3b8d0b`
   and deterministically identifies BTR-E06 without relying on raw stderr;
4. BTR-E06's exact absent source position reaches the accepted `SELECT INTO
   STRICT` `NO_DATA_FOUND` lowering and therefore `F_CARDINALITY` / `CF004`
   before the later present-source packet-membership assertion
   `F_ADMISSION_SOURCE` / `CF201`;
5. the candidate changes only BTR-E06 expected failure ID/SQLSTATE, aligned
   plan/design prose and bounded mismatch telemetry; it does not change any
   scenario fixture, order, population, readback, forbidden effect or authority;
6. canonical current behavior contract is
   `sha256:897e07895116eecedaf8a2506ad10f9f5e5207b7e78e68ab79afb09347018a57`
   and current scenario seal is
   `e7647c498e3ae121653a0c9e0cbf7d0d892ce133f49d40b66a865e4d4a6f25eb`,
   while historical receipts retain their old
   `ee44dbf39c2458fdabc94768e3c3e8cdcc0372c10ae7f0a35709b55301c5d596`
   and `d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`
   claims unchanged;
7. the accepted database body, structural contract, DDL renderer, inert SQL,
   manifest, parse evidence and all six behavior-parent receipts are byte-
   unchanged from `656da985`;
8. mismatch evidence exposes only typed scenario ID, expected/observed SQLSTATE,
   bounded psql exit and the existing digest, never raw stderr or provider,
   patient, product or operational data; hostile schema tests fail closed;
9. `CF201` stable reason is correctly narrowed from missing source to present-
   source mismatch, without changing SQLSTATE admission semantics;
10. AER revision 194 contains exactly 227 closed incidents through AER-0227,
    accurately records the invalid backup cmdlet parameter, attempt-043
    repository mismatch and diagnosis-delimiter assumption, and its pattern
    report is regenerated and deterministic;
11. every changed Python file passes Ruff lint and format, focused tests pass,
    historical/current seal separation is explicit and the exact renderer CF004
    test still passes;
12. the clean verifier checkout does not contain the untracked mutable evidence
    alias and no test improperly depends on it; and
13. no Docker/PostgreSQL run, operational database, applied migration,
    watcher/feed, application/API/Diary wiring, patient/clinical/product data,
    command/write authority, deployment, release, Pages or protected-ref
    boundary opens.

Run these exact checks and wait for completion:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r172 tests\test_raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py::test_renderer_exact_cardinality_maps_zero_and_multiple_to_cf004 tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_043_missing_source_sqlstate_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
git diff --check 656da9851f113c7ab639fc7634307c7be4a32cd6..77afc48114328061c6cd3deef12b46fdf2a51ae6
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
