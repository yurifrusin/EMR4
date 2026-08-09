# Independent veto packet: lifecycle RLS lock visibility and behavior rebind

Date: 2026-08-09

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r132`
- Branch: `codex/review-context-fabric-rls-lock-behavior-3f2473a8`
- Recovery baseline: `e7e7265efd7773e3bf1fabace7af46ceb7d63566`
- Candidate: `3f2473a878aa3c152d75795aeb0b87a7a4c7d633`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 023 correctly exposed a
PostgreSQL RLS policy-combination defect on the lifecycle principal's
`SELECT ... FOR UPDATE`, whether the narrowly repaired policy preserves the
row lock while granting no lifecycle mutation authority, whether the exact
structural/body/artifact/parse parents were safely rebound, and whether the
frozen twenty-scenario behavior contract remains unchanged and eligible for
one later Sol-owned disposable attempt 024.

No behavior runtime is authorized by this review. Do not start Docker or
PostgreSQL.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported or cited contracts, schemas and these canonical
parents:

- the behavior RLS lock-visibility recovery and threat-model delta;
- immutable behavior failure evidence 023 and its bounded diagnosis receipt;
- AER revisions 129-131, AER-0154/AER-0155/AER-0156 and the generated pattern
  report;
- structural migration/transaction contract and schema;
- function/trigger body contract, schema, builder and validator;
- inert renderer, SQL artifact, lowering contract/schema and render manifest;
- parse harness/contract/schema, characterization evidence, terminal exact
  evidence and accepted-source ledger;
- behavior harness, contract/schema and parent-rebind ledger;
- the exact tests named below; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. immutable attempt-023 evidence has file SHA-256
   `de359f9acc731b0127517b6dc14accb9bfe7e9b5ae63b35213cf5d6e160649ee`,
   records `BTR-E01`, SQLSTATE `CF004`, zero of twenty admitted scenarios and
   verified removal/absence of its exact owned container;
3. the bounded diagnostic receipt has file SHA-256
   `7809516d132cdd303f47274028678c9a0e5a26ad7f52c5f810947a5a37771663`
   and coherently proves that lifecycle ordinary `SELECT` saw exactly one
   stream-head row, the exact lifecycle binding was allowed, and otherwise
   identical `SELECT ... FOR UPDATE` returned no row, without persisting raw
   database error text or unrestricted values;
4. PostgreSQL 16 applies both the `SELECT` policy and applicable `UPDATE USING`
   policy to rows selected with `FOR UPDATE`/`FOR SHARE`, so producer-only
   update visibility caused the diagnosed lock-path disappearance rather than
   a missing row or invalid binding;
5. only `pol_cf_01_update USING` now admits `PRODUCER` or `LIFECYCLE`, while its
   `WITH CHECK` remains producer-only; `pol_cf_10_update` and
   `pol_cf_11_update` remain unchanged and do not admit lifecycle;
6. `context_lifecycle` retains zero direct Fabric table DML, zero direct table
   `SELECT`, `NOINHERIT`, `NOBYPASSRLS` and only its closed security-definer
   entry points, so lock eligibility cannot be used as direct write authority;
7. the exact `SELECT ... FOR UPDATE` row lock is preserved; no unlocked-read,
   superuser, RLS-disablement, owner or grant workaround was introduced;
8. structural semantics and hostile tests reject both removal of lifecycle
   from stream-head update `USING` and addition of lifecycle to the write
   check or unrelated policies;
9. structural source is
   `338c30ddb01561ce97a4b9837317e771b555c221`, canonical structural file
   SHA-256 is
   `648acf79c86d16bf7fcd9ad1f88dcab5bc4aded01c4e0084f66c6c36b4adeca1`,
   and body source is `987f64a9f68c8dec2b99d5d39aa74e28411a82fa`
   with canonical body contract SHA-256
   `6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b`;
   no body program, SQLSTATE registry, transaction effect or function/trigger
   meaning changed beyond its structural-parent binding;
10. renderer 2.0.10 recognizes the exact corrected policy semantics and the
    inert artifact remains exactly 412 statements and 1,391,506 canonical LF
    bytes at SHA-256
    `28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800`,
    with render-manifest file SHA-256
    `8ced08cb218b4a19cb1abbf41930db3dcec0ac1e60fa132d38e9fba8c813c49e`;
11. the SQL semantic diff against the preceding accepted artifact is exactly
    lifecycle addition to `pol_cf_01_update USING`, with producer-only
    `WITH CHECK`, statement population, direct grants, functions, triggers,
    relations and role population unchanged;
12. the characterization and terminal exact parse runs used distinct newly
    owned networkless PostgreSQL 16 containers, both were removed with exact-ID
    absence independently observed, and only the terminal run can be accepted;
13. terminal exact parse evidence has file SHA-256
    `e417fc377e6b8e9ff723e21e88b40e41b9cfb2424d2fd6122e404c54bf068611`,
    binds exact parse contract SHA-256
    `2834249d755d83764abf974d524424b958a261f6d8c94808403d4d8bf3a5a1f1`,
    matches all fifteen catalogue digests, and only the `policies` digest
    differs from the preceding accepted proof as expected;
14. the accepted-source ledger binds exact parse evidence source
    `a7a780f9735d3c41095703d464611752f89685d9`, and the behavior contract's six
    parent rows bind that ledger, corrected artifact/manifest, structural/body
    parents and unchanged prerequisite contract exactly;
15. behavior contract canonical SHA-256 is
    `af8f89a18c97663a458f314a34ba2f978392f681f38fa8641c0c9be3b19d9009`;
    all twenty scenario objects and order remain identical with unchanged
    scenario canonical SHA-256
    `eec93b0d67bd70a9640b3000bc63d43a08aa6817b438e0c99dbf2595a69c4c19`
    and category counts `6/4/3/4/3`;
16. AER-0154 accurately records the rejected adapter-method receipt,
    AER-0155 accurately records the repository RLS defect, AER-0156 accurately
    records the rejected unapproved continuation event, register revision 131
    contains 156 incidents and zero open incidents, and none is misattributed
    to Gemini or PostgreSQL;
17. the complete 412-test packet below passes with Ruff check, Ruff format and
    both diff checks; and
18. no Docker execution occurred after the exact parse proof, no mutable failed
    behavior evidence was admitted, and no credential, network, mount, port,
    product, patient, provider, application, migration, watcher/listener,
    command/write, deployment, release, Pages or protected-ref boundary
    widened; HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r132 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_023_rls_lock_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check e7e7265efd7773e3bf1fabace7af46ceb7d63566..3f2473a878aa3c152d75795aeb0b87a7a4c7d633
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, wrong RLS diagnosis, lifecycle
write-authority widening, lost row lock, incomplete parent rebind, scenario
drift, parse-evidence mismatch, widened containment, incomplete deterministic
packet or dirty postcondition. Otherwise return one exact `pass`, stating
findings, commands/counts, HEAD and post-review cleanliness.
