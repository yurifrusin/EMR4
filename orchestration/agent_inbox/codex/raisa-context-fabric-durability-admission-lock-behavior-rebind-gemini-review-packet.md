# Independent veto: admission-lock RLS recovery and behavior rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r164`
- Branch: `codex/review-context-fabric-admission-lock-3cbaa4cb`
- Diagnosed-failure baseline: `444f57b9a343bf3b542bc222b4c11bde49b6ce1a`
- Candidate: `3cbaa4cb68acb78370183947a315f946f8d0ddaa`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently verify the complete diagnosed-failure-to-candidate recovery.
Behavior attempt 037 failed safely because forced RLS allowed a normal
coordinator read of the exact PRIMARY admission but hid the same row from the
contracted `FOR UPDATE` lock. The candidate adds one lock-visibility policy,
reseals the unchanged typed body, regenerates inert SQL, reproduces the exact
PostgreSQL catalogue, rebinds the unchanged twenty-scenario behavior contract
and strengthens BTR-R03 to deny direct coordinator admission UPDATE.

Decide whether the repair restores the required row lock without creating
direct mutation, cross-practice, observer, command, runtime or product
authority. Prior receipts are context, not acceptance; rerun the checks.

## Exact allowed surface

Review only AGENTS.md and the following directly cited surface:

- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-plan.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-design.md`
- `docs/security/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal-threat-model-delta.md`
- the admission-lock recovery, structural/body/inert/parse rebind and behavior
  parent-rebind documents plus their threat-model deltas;
- structural contract/schema and exact structural tests;
- typed function/trigger body contract and focused tests;
- inert SQL, manifest, renderer and focused tests;
- parse contract/schema/harness/tests and the two immutable admission-lock
  characterization/reproduction evidence files;
- behavior contract/schema/harness/tests;
- immutable failure and diagnosis evidence 037 plus its diagnosis script/test;
- exact parse Sol acceptance, AER-0209/AER-0210, revision 182, register,
  pattern report and focused register tests; and
- current Ariadne receipts named by this packet.

Do not inspect protected holdouts, historical Diary material, `docs/branding/`,
patient/clinical/product-derived data or unrelated paths. Do not use
repository-wide content search outside the exact allowlist.

## Required challenges

Verify and report:

1. exact clean HEAD before/after and exact baseline-to-candidate diff;
2. failure 037 file SHA-256
   `a5767ddcc04643a949ea465abadd94fdb8dbc28c272bdf19808abc3e7759b852`,
   attempt `d38e0bd5b2621bcea59d5397`, `BTR-E04`, `CF004`, function line
   307, inert SQL line 1262, `expected=20, observed=0, passed=0` and exact
   cleanup absence;
3. diagnosis 037 file SHA-256
   `97126e0da6ab6b2e616084f96951e69b11540d338fe709f1f7364fa17ac7872b`
   proves the preceding normal read saw the PRIMARY while the exact
   `apply_durability_transition_v1.lock_primary` `FOR_UPDATE` node could not;
4. `pol_cf_04_update_lock` is permissive `FOR UPDATE TO PUBLIC`; `USING`
   admits exactly COORDINATOR with exact session-user/practice/source/time
   binding; `WITH CHECK` repeats that predicate and ends `AND FALSE`;
   OBSERVER and every unlisted capability remain excluded;
5. the coordinator retains empty direct table DML, entry-point grants and
   typed body semantics are unchanged, and hostile structural tests reject
   missing, widened, foreign-capability, non-PUBLIC or mutable policy forms;
6. structural digest is
   `sha256:80d5b57eadef0e6ede54c48fc842fe5567723c0a9cdebe288efbf63048c4b3ac`
   at exact source `3a19167e13ac01996180e1b5ada2a6e2ae7e135f`;
7. body digest is
   `sha256:8124957e32657076c3befc96a7b5e8770dcd37fcb5b91e33c136f01cbf2dd5ea`
   at exact source `f42558c14c59c2d37a5b96d4a880941f26038d26`, with no body-program
   semantic change;
8. inert SQL source `b0339bed1090f1f04c198ca0fb2bdf2932ca702c`
   is exactly 1,436,426 LF bytes, 423 statements and SHA-256
   `1ab976d0555021aa6ec41778b2c3de6ef27105f17f8d1d941b714006da93b1d5`;
   manifest SHA-256 is
   `6adab0a48917c518df81035befe0991f15cba56950713f7329a08054a35f5dd7`;
9. immutable characterization evidence SHA-256 is
   `21c9139cf194f8077837de0f97d07a189e89bc5826413a7ddae27ae14a0c18fb`,
   the sole catalogue change is policy count 47 and policies digest
   `sha256:4e5405911b0bf1fc98cd203078639765d0fb37e708e1d2c6c7a2b119104c092d`;
10. immutable exact parse evidence SHA-256 is
    `aeaaafc309b2f083688988aed21f77f39283b2c64d391133e8223effc1224de5`,
    all 15 digests match under parse contract
    `sha256:c48d34397de7c2bb433a28af2c064acdf780877933ee9d7edb28c2cc2c9644e5`,
    rollback passes and exact cleanup is proved;
11. behavior contract canonical digest is
    `sha256:a16769b43c8345b3c79cc79d1ca26e4cd0b2d7095515d2b13bc7e21cb27b5b8e`
    and binds exactly the six repaired parents;
12. the twenty scenario objects/order, expected SQLSTATEs and category counts
    `6/4/3/4/3` are unchanged;
13. BTR-R03 uses eight distinct fresh connections and its new
    `coordinator_admission_direct_update` cell targets the exact synthetic
    PRIMARY with a no-op UPDATE that must fail `42501`; this is still one RLS
    scenario, never a twenty-first scenario or granted direct write;
14. revision 182 correctly closes AER-0209 and AER-0210, the register contains
    210 closed incidents and its pattern report is exact;
15. no mutable behavior/parse evidence, Docker runtime, credential, network,
    mount, port, application/API/Diary surface, watcher/listener/feed,
    product/patient data, provider, deployment, release, Pages or protected
    ref boundary widened;
16. all tests below, Ruff and diff checks pass; and
17. candidate HEAD and checkout remain exact and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r164 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 444f57b9a343bf3b542bc222b4c11bde49b6ce1a..3cbaa4cb68acb78370183947a315f946f8d0ddaa
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, access patient/clinical/product
or protected data, inspect `docs/branding/`, move refs or accept your own
output.

Return `fail` for any P0-P2 finding, authority widening, parent/scenario drift,
test failure, dirty postcondition or incomplete packet. Otherwise return exact
`pass` with findings, commands/counts, exact HEAD and cleanliness.
