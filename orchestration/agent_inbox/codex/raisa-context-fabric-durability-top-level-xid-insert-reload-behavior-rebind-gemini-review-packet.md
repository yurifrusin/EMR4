# Independent veto packet: top-level-XID insert/reload recovery and behavior rebind

Date: 2026-08-09

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r107`
- Branch: `codex/review-context-fabric-top-level-xid-behavior-acae3131`
- Recovery baseline: `ef03e31e82d11e8e54650d795c243e28a76e2a06`
- Candidate: `acae3131c0e583c8d4d344c9419f43bda9a82e9f`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 022 correctly exposed a
renderer-authored PL/pgSQL subtransaction `xmin` mismatch, whether renderer
2.0.10 repairs every typed insert-or-reload write without weakening the exact
top-level-XID provenance fence, whether a separate characterization and
terminal PostgreSQL-16 parse/catalogue sequence accepted the corrected
artifact, and whether the frozen twenty-scenario behavior contract was rebound
only to those accepted parents.

No behavior runtime is authorized by this review. The successful veto is a
precondition for one later Sol-owned disposable behavior attempt.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported or cited contracts, schemas and these canonical
parents:

- the top-level-XID recovery and threat-model delta;
- immutable behavior failure evidence 022 and its bounded diagnosis receipts;
- AER revisions 126-127, AER-0151/AER-0152 and the generated pattern report;
- inert SQL, render manifest, structural contract, typed body contract,
  parse/prerequisite contracts and accepted parse evidence;
- the inert renderer, parse harness and behavior harness;
- the accepted-source ledger and behavior contract;
- the exact tests named below; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. immutable attempt-022 evidence validates, has file SHA-256
   `6ae6ef74c6a44c8f022f54f54bbc31d6a867a6f9953b7ee52ca34e68bf71f224`,
   records `BTR-E01`, SQLSTATE `CF105`, zero of twenty admitted scenarios and
   verified removal/absence of exact container
   `fee2a57a1f0056667fadba326f441df301beade22a1e03391ee47fe8c7a33484`;
3. diagnosis 022a/022c coherently proves the failed conjunct in
   `cf_fence_stream_head_v1` was exact tuple `xmin` versus current top-level
   XID32 while `last_position = 0` and `stream_epoch = 1` both passed, without
   persisting raw database text or unrestricted values;
4. PostgreSQL creates a subtransaction for a PL/pgSQL block containing an
   `EXCEPTION` clause while `pg_current_xact_id()` remains the top-level XID,
   so renderer 2.0.9's write-bearing exception block could author the rejected
   subtransaction tuple and the fence itself must remain unchanged;
5. renderer 2.0.10 changes all twenty-one typed
   `INSERT_OR_RELOAD_COMPARE` lowerings to exact `INSERT ... ON CONFLICT ON
   CONSTRAINT ... DO NOTHING RETURNING`, followed only on `NOT FOUND` by a
   read-only exact-winner `SELECT ... INTO STRICT`; no write-bearing
   `unique_violation` handler or `cf_constraint_name` diagnostic remains;
6. every conflict target is the exact derived named constraint; generic or
   wrong-target `ON CONFLICT DO NOTHING`, zero/multiple winner paths and
   unrelated uniqueness failures remain rejected rather than absorbed;
7. the exact top-level-XID expression and its nineteen typed consumers are
   unchanged, the structural and typed-body contracts are byte-identical to
   baseline, and no savepoint/subtransaction provenance broadening occurred;
8. statement count remains `412`; corrected inert SQL is exactly `1,391,453`
   canonical LF bytes at SHA-256
   `25744edad60b0f76083cb6bb0d35a077b58cb9cad1fcff23089d2bcb064107cb`,
   with render-manifest SHA-256
   `d597e0df4c30bd7c5e3745345a34bee712632fb8803df7afe2762ad53fef6e57`;
9. the nonpassing characterization attempt
   `c245e527106f271ffcc6d27d` and the separate terminal attempt
   `8691e2df62f225e59e5726ef` used distinct newly owned containers, both were
   removed with absence verified, and only the terminal evidence can emit the
   accepted parse result;
10. accepted parse evidence has file SHA-256
    `83ea56186636b2ffb7dfce8c3d8d303bc489fce8d9e5301ccbe0e3b8cde0629a`,
    binds parse contract SHA-256
    `d482ab2c4b96e3bfa854e4c723e9891c2b4b8ac9670db2f73729207ede345919`,
    matches every frozen catalogue digest, proves the fixed invalid-copy
    rollback with zero schema/role residue and proves exact removal/absence of
    terminal container
    `9aafcf3721ae6922a36478232aad8898b88d280b315dc2c7740fe2b7256e8d64`;
11. the parse harness now overwrites accepted evidence only for the exact pass
    result and routes every later failure to a distinct fixed failure path, so
    a failed rerun cannot destroy the last accepted pass artifact;
12. the accepted-source ledger binds exact parse evidence source
    `2d246443f5dc66a221c33d3dc1547f0c4a4f4fcb`, and the behavior contract's six
    parent rows bind that ledger, renderer/artifact/manifest, unchanged
    structural/body contracts and current prerequisite contract exactly;
13. the behavior contract's canonical SHA-256 is
    `2fa4840da97439cbfe143be407a30de995244db2cfc5a69cfe54bb5580354358`;
    all twenty scenario objects and order remain identical with unchanged
    scenario-array SHA-256
    `7c8709c2ec1c0eb69da86fe037f551355ada6c1294e2ca4f2ce7f15ad89be5b3`
    and category counts `6/4/3/4/3`;
14. AER-0151 accurately records the renderer repository defect, AER-0152
    accurately records the rejected unapproved `pre_execution` continuation
    event and its corrected `pre_worker_dispatch` receipt, register revision
    127 contains 152 incidents and zero open incidents, and neither incident
    is misattributed to Gemini or PostgreSQL;
15. no Docker execution occurred after the terminal parse proof and no
    credential, network, mount, port, product, patient, provider, application,
    migration, watcher/listener, command/write, deployment, release, Pages or
    protected-ref boundary widened;
16. all 404 deterministic tests in the exact packet below, Ruff check, Ruff
    format check and both diff checks pass; and
17. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r107 tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check ef03e31e82d11e8e54650d795c243e28a76e2a06..acae3131c0e583c8d4d344c9419f43bda9a82e9f
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, wrong failure diagnosis,
weakened top-level-XID fence, incomplete targeted conflict lowering, typed
contract or scenario drift, parse-evidence mismatch, widened containment,
incomplete deterministic packet or dirty postcondition. Otherwise return one
exact `pass`, stating findings, commands/counts, HEAD and post-review
cleanliness.
