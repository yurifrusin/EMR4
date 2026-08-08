# Independent veto packet: durability lifecycle-registration RLS recovery

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r101`
- Branch: `codex/review-context-fabric-registration-rls-ae5b33`
- Baseline: `ee894c9d8796ab6f656bf341141e167a58554e4d`
- Candidate: `ae5b33c1e5d1f9b12d6f10cefb1c9e577e72189c`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 018 correctly exposed a forced-
RLS denial during lifecycle generation registration, whether the exact six-
policy structural correction is least-privilege and complete, whether its
typed-body and inert-artifact descendants preserve meaning, whether exact
PostgreSQL parse/catalogue evidence passes with complete cleanup, and whether
the frozen twenty-scenario behavior contract is rebound only to those accepted
parents before attempt 019.

## Allowed review surface

Review the exact baseline-to-candidate diff and only changed files plus their
directly cited contracts, schemas, harnesses and tests:

- registration-RLS recovery, threat delta, body-parent rebind, artifact rebind,
  parse rebind/characterization/closeout and behavior-rebind documents;
- AER revision 118, AER-0141, register and generated pattern report;
- behavior failure evidence 018, immutable catalogue characterization and
  current parse/catalogue pass evidence;
- structural contract, typed body contract, inert SQL, render manifest,
  behavior contract and synthetic prerequisite contract;
- structural/body builders and validators, inert renderer, parse harness and
  behavior harness;
- the exact tests named below; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a repository-
wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. attempt-018 evidence validates, has file SHA-256
   `aeb88e2f404adb62300c0c0574b114c4254ccceb047140e75dd55eac6de61bc7`,
   records `BTR-E01`, SQLSTATE `42501`, zero scenarios and verified exact-ID
   cleanup;
3. the accepted lifecycle entry point runs as a security-definer owner but
   forced RLS still evaluates the exact session-user binding; no direct table
   grants, `BYPASSRLS`, role membership or owner bypass are introduced;
4. exactly these policies add `LIFECYCLE`, and only to the necessary operation:
   `pol_cf_01_select`, `pol_cf_01_insert`, `pol_cf_10_select`,
   `pol_cf_10_insert`, `pol_cf_11_select`, `pol_cf_11_insert`; matching UPDATE
   policies and every other policy remain unchanged;
5. the structural contract has semantic SHA-256
   `d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`
   and canonical-text SHA-256
   `2463efb28175d4dc8232c08e4401565ff00663698e072aa931144aa37cf0d53f`;
   the body contract changes only its structural-parent coordinates, retains
   all program/effect/signature meaning, has semantic SHA-256
   `422b7cd5203893ecd2269c9b2dbf4018ed359661d5ebe962de55afffb03c340c`
   and canonical-text SHA-256
   `39a841d357388ca8cb0d1e40c73218af3e59e78090f882169e000b3ef16fa2eb`;
6. renderer 2.0.7 produces exactly 412 statements and 1,402,659 LF bytes at
   SHA-256
   `34d321adce220a94473e3cd74173f7b0ffc37441b2e4dd24699ca18b86c7e760`,
   with no unrelated role, function, trigger, relation or privilege drift;
7. AER-0141 coherently records the SQLSTATE-42501 lifecycle-registration RLS
   incident, revision 118 contains 141 incidents and zero open incidents, and
   no unsupported causal/provider claim is made;
8. immutable characterization evidence has file SHA-256
   `d46af8f0ae45f0b79b0ca81a8a09728b046747486399c8ac0646772073657726`,
   cannot pass acceptance, changes only the policy projection digest to
   `7c847b9d0e153bb02101bc3704d33d72e8aefdf4cfc911e0b092149393cc1b37`
   and proves exact cleanup;
9. exact parse evidence has file SHA-256
   `44f4ba03cc25abfc437ca3385b7f8e0c335477dec0724d3726058f78d37170bc`,
   proves the expected `42601` rollback with zero role/schema residue, matches
   all 17 exact catalogue digests, binds the corrected parent and proves exact
   cleanup/absence;
10. behavior contract canonical SHA-256 is
    `7d58d870444274e7bfa11be32585acb0164901b79cbc95c9542721f54d4867df`,
    all twenty scenario objects/order remain identical to baseline with
    category counts `6/4/3/4/3`, and only six parent-coordinate objects change;
11. the registry-barrier fixture remains exactly one alpha row at revision
    zero and `BTR-E01` still expects exact revision three after three serial
    registrations;
12. the active deterministic packet is exactly 386 passing checks. The frozen
    historical body-continuity equality module is deliberately excluded because
    it asserts obsolete Continuity 230/AER 81 artifacts; verify it was not
    modified or used as current evidence;
13. Ruff and the exact diff check pass, and no Docker, credential, network,
    mount, port, data, provider, product, deployment, release, Pages or
    protected-ref boundary widened; and
14. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
git diff --check ee894c9d8796ab6f656bf341141e167a58554e4d..ae5b33c1e5d1f9b12d6f10cefb1c9e577e72189c
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong evidence hash/coordinate, excessive
RLS widening, typed-contract or scenario drift, parse-evidence mismatch,
widened containment, incomplete deterministic packet or dirty postcondition.
Otherwise return one exact `pass`, stating findings, commands/counts, HEAD and
post-review cleanliness.
