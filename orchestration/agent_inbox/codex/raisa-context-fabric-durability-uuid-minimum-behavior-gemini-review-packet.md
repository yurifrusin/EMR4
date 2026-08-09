# Independent veto packet: UUID minimum and behavior parent rebind

Date: 2026-08-09

Decision required: exactly one terminal structured `pass` or
`revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r136`
- Branch: `codex/review-context-fabric-uuid-minimum-behavior-6672c547`
- Accepted pre-failure baseline: `9d8c0ad9c62da749ff7331ebd9cb94f07ed142e2`
- Candidate: `6672c547fe46bf304e7dceddb0dd01704bf68064`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 025 correctly exposed a missing
PostgreSQL UUID minimum aggregate at BTR-E02, whether renderer 2.0.12 repairs
only that typed lowering without weakening deterministic minimum semantics,
whether fresh characterization and separate exact parse proofs bind the
repaired artifact, and whether the behavior contract's six parents were
rebound without changing any of its twenty ordered scenarios. A `pass` makes
one later Sol-owned disposable behavior attempt 026 eligible; it is not
acceptance of that future run.

No behavior runtime is authorized by this review. Do not start Docker or
PostgreSQL.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported or cited contracts, schemas and these canonical
parents:

- immutable failure-025 evidence, bounded diagnosis receipt, UUID recovery
  plan and threat-model delta;
- AER revisions 136-137, AER-0161/AER-0162 and the generated pattern report;
- structural migration/transaction and immutable function/trigger body
  contracts and schemas;
- inert renderer, SQL artifact, lowering contract/schema and render manifest;
- parse harness, contract/schema, preserved interval exact proof, UUID
  characterization, UUID terminal exact evidence and accepted-source ledger;
- behavior harness, contract/schema, UUID parent-rebind ledger and frozen
  scenario definitions;
- the verifier-launch receipt guard and its tests;
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
2. immutable attempt-025 evidence has file SHA-256
   `b963933df05c418456fdc1e101a7254a617ba743a4cb4b03888caf0aac547ba2`,
   records BTR-E02, SQLSTATE `42883`, zero completed scenarios and verified
   removal/absence of exact container
   `43bf5d122670f424821cf00511d2ee21404f0b66c4d19ead9e0bdbf45ea833da`;
3. the bounded diagnosis receipt has file SHA-256
   `d9795197a5e088e3255c41c8cef12f5cbce8e7a34c0ee38de5184c5e51de2fe0`,
   binds attempt 025 exactly, requires all five fixed prerequisites to
   resolve, proves the old integer-times-interval signature remained absent
   and unexecuted, releases only
   `repository_function::pg_catalog.min`, persists no raw error text and
   verifies exact-ID cleanup;
4. the first attempt-025 diagnosis stopped without a durable candidate because
   its inherited historical allowlist was incomplete; AER-0161 accurately
   records that harness undercoverage and the corrected classifier admits
   only one repository-bounded function call or one safe type/operator
   signature while still hashing raw text;
5. PostgreSQL 16 lacks `min(uuid)` while the accepted typed body uses two UUID
   `MIN_FIELD` expressions for `producer_bindings.stream_id` and two valid
   bigint minimum expressions; the failure is coherent and is not attributed
   to Gemini, a provider or environment readiness;
6. renderer 2.0.12 retains `pg_catalog.min` only for exact bigint, lowers UUID
   minimum to an ordered `pg_catalog.unnest` subquery with ascending order,
   `NULLS LAST` and `LIMIT 1`, and rejects every other result type;
7. the independent recognizer and hostile tests reject reintroduction of
   `pg_catalog.min(s.stream_id)`, unsupported types and malformed or widened
   minimum shapes; no untyped SQL or caller-selected expression was added;
8. structural source remains
   `338c30ddb01561ce97a4b9837317e771b555c221` and body source remains
   `987f64a9f68c8dec2b99d5d39aa74e28411a82fa`; no typed body program,
   SQLSTATE, transaction effect, entry point, trigger, role, policy or
   authority meaning changed;
9. renderer source is `c97ea3eb935997ace3586aa2ff52cf33dabbfd6a`;
   the inert artifact is exactly 412 statements and 1,391,670 canonical LF
   bytes at SHA-256
   `eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8`,
   with render-manifest file SHA-256
   `4e3d80f2855bcf97f9e0fdce9630b42b9f2b67454df77e6954cbb79e8e3aac11`;
10. the SQL semantic change against renderer 2.0.11 is only the two UUID
    minimum lowerings, while the two bigint minima, statement population,
    relations, roles, grants, RLS policies, functions and triggers remain
    unchanged and `.gitattributes` forces the artifact to LF;
11. the non-accepting characterization used attempt
    `29d2df4202acb1f879cd4b4a`, has file SHA-256
    `db86a77bc81f12a461161c807710ba8a42eabfa76080289704d5819dabee35ba`,
    records `catalogue_characterization_required`, and preserved all
    seventeen catalogue query digests from the preceding exact proof;
12. characterization and terminal exact parse runs used distinct newly owned
    networkless PostgreSQL 16 containers, both were removed with exact-ID
    absence independently observed, and only the terminal run is accepted;
13. terminal exact parse evidence uses attempt
    `988bb667765158c33e219d8d`, has file SHA-256
    `f14c406ca460ba893e66fed3150e759f63d9631c976a95fbb03faae7f1f381c8`,
    binds exact parse contract SHA-256
    `fd8256d4906e79367d280f5ba945c8b2ccb0f01f20790cb43ae68f47496dbdc4`,
    matches all seventeen characterized query digests and verifies exact
    container removal/absence;
14. the accepted-source ledger has file SHA-256
    `3bc7276360e83e81e8a0de95294d1a27b8946476ddf184663ef1e34280bf3a9c`
    and binds exact parse evidence source
    `718730875b9b5c590a08d0e5be842f8b180a73ce`;
15. the behavior contract's six parents bind that accepted-source ledger,
    renderer artifact/manifest, unchanged structural/body sources and
    unchanged prerequisite contract exactly;
16. behavior contract canonical SHA-256 is
    `b6d8732b655d038de719f34f59854a2463f3ccfc89e589264f13a8dced435c57`;
    all twenty scenario objects and order remain identical at scenario
    canonical SHA-256
    `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`
    with category counts `6/4/3/4/3`;
17. AER-0162 accurately records the repository UUID aggregate lowering
    defect, register revision 137 contains 162 incidents with none open, and
    neither AER-0161 nor AER-0162 is misattributed;
18. the verifier launcher requires one passed five-source orchestrator
    receipt before reading this packet or invoking Antigravity and records
    that receipt's SHA-256 in its worker receipt;
19. API Spine direction remains read-model GraphQL plus typed deterministic
    command authority, while this candidate adds no API operation, GraphQL
    mutation, capability, product/runtime wiring or model-to-database path;
20. the complete packet is exactly 484 tests and all pass, with Ruff check
    and Ruff format on every named Python file plus both diff checks clean;
21. no Docker execution occurs during review, no mutable failed behavior
    evidence is admitted, and no credential, network, mount, port, product,
    patient, provider, application, migration, watcher/listener,
    command/write, deployment, release, Pages or protected-ref boundary
    widens; HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r136 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\ariadne_antigravity.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_antigravity.py
git diff --check 9d8c0ad9c62da749ff7331ebd9cb94f07ed142e2..6672c547fe46bf304e7dceddb0dd01704bf68064
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface other than this single verifier
model invocation, access patient/clinical/product or protected data, inspect
`docs/branding/`, move refs or accept your own output.

Return `revision_required` for any P0-P2 finding, invalid UUID lowering,
evidence mismatch, scenario drift, API/authority widening, invalid dispatch
receipt, incomplete 484-test packet or dirty postcondition. Otherwise return
one exact structured `pass`, stating findings, commands/counts, HEAD and
post-review cleanliness.
