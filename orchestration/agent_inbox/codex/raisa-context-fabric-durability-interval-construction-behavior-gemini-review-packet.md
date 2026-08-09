# Independent veto packet: durability interval construction and behavior rebind

Date: 2026-08-09

Decision required: exactly one terminal structured `pass` or
`revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r134`
- Branch: `codex/review-context-fabric-interval-behavior-308f49ce`
- Accepted pre-failure baseline: `b8bc7ca6e0ca27329ac098a05642641480b684fb`
- Candidate: `308f49ceb04d243981110270f828c453f796f055`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 024 correctly exposed the
invalid PostgreSQL `integer * interval` construction at BTR-E02, whether
renderer 2.0.11 and the independent authored-synthetic fixture repair only
that defect with typed `make_interval` calls, whether fresh characterization
and exact parse proofs bind the repaired 412-statement artifact, and whether
the behavior contract's six parents were rebound without changing any of its
twenty ordered scenarios. A `pass` makes one later Sol-owned disposable
behavior attempt 025 eligible; it is not acceptance of that future run.

No behavior runtime is authorized by this review. Do not start Docker or
PostgreSQL.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported or cited contracts, schemas and these canonical
parents:

- failure-024 evidence, bounded undefined-symbol diagnosis, recovery plan and
  threat-model delta;
- AER revisions 133-134, AER-0158/AER-0159 and the generated pattern report;
- structural migration/transaction and immutable function/trigger body
  contracts and schemas;
- inert renderer, SQL artifact, lowering contract/schema and render manifest;
- parse harness, contract/schema, prior accepted RLS proof, characterization,
  terminal exact evidence and accepted-source ledger;
- behavior harness, contract/schema, parent-rebind ledger and frozen scenario
  definitions;
- API Spine ADR/programme, Context Fabric GraphQL read contract, capability
  manifest and async integration contract for boundary conformance;
- the exact tests named below; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. immutable attempt-024 evidence has file SHA-256
   `bc2efc6fffea47e8104324c822bd6c1afde28f746b05b2a5bff925dbbfe7f57b`,
   records BTR-E02, SQLSTATE `42883`, zero of twenty complete scenarios and
   verified removal/absence of exact container
   `61a367f04b85b89b35af3abd5fb5390e94a0a44a7d290022554f443ea8c5f86a`;
3. the bounded diagnosis receipt has file SHA-256
   `a2169d1be7138cc7975dfa5ad41ca42ee5c9f27041808b3481902c938f090b61`,
   binds attempt 024 exactly, releases only six fixed resolution booleans and
   the missing `pg_catalog.int4_times_interval` identifier, persists no raw
   error text and verifies exact-ID cleanup;
4. PostgreSQL 16 has `timestamptz + interval` and typed `make_interval`
   constructors but no diagnosed `integer * interval` signature, and the
   attempt-024 failure is therefore coherent rather than attributed to a
   provider, Gemini or environmental readiness;
5. renderer 2.0.11 lowers minutes through
   `pg_catalog.make_interval(mins => integer_expression)` and seconds through
   `pg_catalog.make_interval(secs => (integer_expression)::pg_catalog.float8)`,
   while BTR-E02 independently constructs its fixed duration with named
   `mins`;
6. the independent recognizer and hostile tests reject every predecessor
   numeric-times-`make_interval` spelling, and no untyped raw SQL, changed
   units or broadened expression family was introduced;
7. structural source remains
   `338c30ddb01561ce97a4b9837317e771b555c221` with canonical structural
   SHA-256
   `648acf79c86d16bf7fcd9ad1f88dcab5bc4aded01c4e0084f66c6c36b4adeca1`,
   and body source remains `987f64a9f68c8dec2b99d5d39aa74e28411a82fa`
   with canonical body SHA-256
   `6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b`;
   no typed body program, SQLSTATE, transaction effect, entry point, trigger,
   role, policy or authority meaning changed;
8. renderer source is `8c307d28323c68744338e2290879994e4980b2dd`;
   the inert artifact is exactly 412 statements and 1,391,614 canonical LF
   bytes at SHA-256
   `c113b2480106441043562412ee3135d2a79bd56c76bb5bc2705734d9e5f8cf51`,
   with render-manifest file SHA-256
   `7a0c5d15e65a4631cf9b590f7c7af67f2103f69ebe05fb2dd9ad5f002e1d1b2d`;
9. the SQL semantic diff against the preceding accepted RLS artifact is only
   the two interval-construction spellings, with statement population,
   relations, roles, grants, RLS policies, functions and triggers otherwise
   unchanged, and `.gitattributes` forces the artifact to LF;
10. the non-accepting characterization used attempt
    `867040b632062d4ed01003e0`, has file SHA-256
    `257daa83f9d45c9397a3666fa54ee906016fd3fa4924d58af2269f3316b65139`,
    records `catalogue_characterization_required`, and preserved all seventeen
    catalogue query digests from the preceding accepted RLS proof;
11. characterization and terminal exact parse runs used distinct newly owned
    networkless PostgreSQL 16 containers, both were removed with exact-ID
    absence independently observed, and only the terminal run is accepted;
12. terminal exact parse evidence uses attempt
    `6b03a15af03f68f6686d8f8a`, has file SHA-256
    `3bb1c5dd63f6b12566869a95abdd1beeaf7a317b045845d5ee4cdcef0eeee4d9`,
    binds exact parse contract SHA-256
    `e1c3b23bf2731f366a1eab342185a6f26eeb638a0a767fcdd391438b5e116e40`,
    matches all seventeen characterized query digests and verifies exact
    container removal/absence;
13. the accepted-source ledger has file SHA-256
    `65d98a18fd8d5e119d549f19027a6343f8d01784995924079855d6336b8926eb`
    and binds exact parse evidence source
    `b0311480bb378553574b039ea536a003bd7ef382`;
14. the behavior contract's six parents bind that accepted-source ledger,
    renderer artifact/manifest, unchanged structural/body sources and
    unchanged prerequisite contract exactly;
15. behavior contract canonical SHA-256 is
    `227d0bafe8d55cf935a2ebea9b8924e2d6b7d632f054950ddbff75fad45a66f6`;
    all twenty scenario objects and order remain identical at scenario
    canonical SHA-256
    `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`
    with category counts `6/4/3/4/3`;
16. AER-0158 accurately records the first diagnostic parser undercoverage,
    AER-0159 accurately records the repository renderer/fixture defect,
    register revision 134 contains 159 incidents and zero open incidents, and
    neither incident is misattributed to Gemini or PostgreSQL;
17. API Spine direction remains read-model GraphQL plus typed deterministic
    command authority, while this candidate adds no API operation, GraphQL
    mutation, capability, product/runtime wiring or model-to-database path;
18. the complete 463-test packet passes, with Ruff check and format on every
    modified candidate Python file, `tests/test_api_spine_artifacts.py`
    passing tests/lint without unrelated formatting churn, and both diff
    checks clean; and
19. no Docker execution occurs during review, no mutable failed behavior
    evidence is admitted, and no credential, network, mount, port, product,
    patient, provider, application, migration, watcher/listener, command/write,
    deployment, release, Pages or protected-ref boundary widens; HEAD and
    worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r134 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check b8bc7ca6e0ca27329ac098a05642641480b684fb..308f49ceb04d243981110270f828c453f796f055
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, incorrect root cause, invalid
interval lowering, incomplete parent rebind, scenario drift, parse-evidence
mismatch, API/authority widening, incomplete deterministic packet or dirty
postcondition. Otherwise return one exact structured `pass`, stating findings,
commands/counts, HEAD and post-review cleanliness.
