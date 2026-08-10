# Independent veto packet: durability recovery-anchor lock visibility

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r161`
- Branch: `codex/review-context-fabric-anchor-lock-263c1ca8`
- Baseline: `978f54205966d412a9a5ead03b1c2c16ca46c5e0`
- Candidate: `263c1ca833dfdc53d5db32c6d57caeadb1edd20d`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 036 correctly exposed a
forced-RLS row-lock visibility defect, whether the added recovery-anchor
UPDATE policy permits only the row-lock semantics required by the existing
coordinator/lifecycle functions while preserving append-only denial, whether
all descendants are exactly rebound, and whether the next disposable behavior
attempt is safe to admit.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported/cited contracts, schemas and canonical parents:

- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-anchor-lock-parent-rebind.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-anchor-lock-rls-recovery.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-anchor-lock-rls-rebind.md`;
- the matching threat-model delta;
- behavior failure and diagnosis evidence 036;
- structural contract/schema, typed body contract, inert SQL and manifest;
- parse contract, immutable anchor-lock characterization and exact reproduction;
- behavior contract, harness and their exact tests;
- the anchor-lock diagnosis script/test;
- AER revisions 175-177, incidents AER-0202 through AER-0205 and the pattern report; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. failure evidence 036 validates at file SHA-256
   `662022a5d0d3744a91397b6a6b8d89e0bfc488631e88691053a7536d914de75c`,
   records scenario `BTR-E04`, SQLSTATE `CF004`, exact function
   `emr4_context_fabric.apply_durability_transition_v1`, function line 299,
   four passed scenarios and verified exact cleanup;
3. diagnosis evidence validates at file SHA-256
   `430de45959a852a146e4f3bb8f88c2ee5fdd1ce193b8d9b833440df9fd91c63b`
   and maps line 299 to the `NO_DATA_FOUND` branch immediately after the
   `context_recovery_anchor ... FOR SHARE` query, while the preceding plain
   SELECT proves one anchor existed;
4. the prior structural contract had only SELECT and INSERT recovery-anchor
   policies, and PostgreSQL forced-RLS row locking requires UPDATE policy
   visibility even for `FOR SHARE`;
5. new `pol_cf_08_update_lock` is permissive, `FOR UPDATE TO PUBLIC`, binds
   only the same practice/stream locator through exact COORDINATOR or LIFECYCLE
   capability, and its `WITH CHECK` repeats that exact predicate plus
   `AND FALSE`; no role receives direct table DML and no entry-point grant or
   function-body instruction widens;
6. hostile structural tests reject a missing policy, a widened check, a
   foreign capability and any role other than PUBLIC; behavior BTR-R03 now
   separately denies direct recovery-anchor UPDATE to both coordinator and
   lifecycle on fresh connections;
7. the typed body program is semantically unchanged and only rebound to
   structural digest
   `6802a7355e62d9d29f735a4c0703e90f2c9bcfaa4606d694070fa62380dc741c`;
   its sealed contract digest is
   `b54b2e6800b4484f84b2c7ba57566ecfe8c04b9a8c8e91ac6bd67be8f22b5840`;
8. inert SQL is exactly 1,435,884 LF bytes, 422 statements and SHA-256
   `550336e145eac6ac004447d05ea3e72d970f6d8283d3af2689aed62cfff92bc6`;
   manifest SHA-256 is
   `95a5c0a613329bd8e6f103130b217a73d597e4e065ca547f658f96db72e8c205`;
9. characterization evidence has file SHA-256
   `e1568e1218fc9663b1490349828a7ea40f5da933e9db0b7b7271164c8981e968`;
   compared with the preceding accepted generation, only the policies digest
   changed and policy count is exactly 46;
10. exact reproduction evidence has file SHA-256
    `28be342cec5fb011a128027e090ebf206be9af034e82596fa69c8cef4fd2d0c0`,
    matches all 15 bound digests under contract digest
    `ce968baca442a3a9c3a3b0a6a13e635115378ec91434bd29baaf58dce07786f3`,
    proves expected atomic rollback and exact cleanup/absence;
11. the behavior contract binds all six exact accepted parents and has
    canonical SHA-256
    `ade8a499d67baa06f23e37ae80cacebe3c6a7b647715f83ca3ee8bf0edcf4e65`;
    all twenty scenario objects/order remain identical to baseline with
    category counts `6/4/3/4/3` and canonical scenario population SHA-256
    `7c8709c2ec1c0eb69da86fe037f551355ada6c1294e2ca4f2ce7f15ad89be5b3`;
12. AER-0202 accurately records the repository defect, AER-0203 through
    AER-0205 record bounded orchestration corrections without unsupported
    causation, and the register/pattern report remain coherent and closed;
13. no Docker runtime, credential, network, mount, port, data, product,
    deployment, release, Pages or protected-ref boundary widened;
14. the focused tests below, Ruff and diff checks pass; and
15. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r161 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 978f54205966d412a9a5ead03b1c2c16ca46c5e0..263c1ca833dfdc53d5db32c6d57caeadb1edd20d
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product
or protected data, inspect `docs/branding/`, move refs or accept your own
output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong evidence hash/coordinate, policy
widening, direct-DML authority, parent or scenario drift, parse-evidence
mismatch, widened containment, incomplete deterministic packet or dirty
postcondition. Otherwise return one exact `pass`, stating findings,
commands/counts, HEAD and post-review cleanliness.
