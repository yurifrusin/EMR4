# Independent veto: coordinator outbox visibility and exact behavior outcomes

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r166`
- Branch: `codex/review-context-fabric-outbox-result-marker-ede9bfa`
- Diagnosed-failure baseline: `810a9dc11bdb39f76f70a6b65cb8afe10732e612`
- Candidate: `ede9bfad1a35f34c13148354af54881e5037ba3f`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently verify the complete failure-038-to-candidate recovery. Behavior
attempt 038 reached `BTR-E04` but the coordinator's security-definer transition
could not see its exact source outbox row under forced RLS. The function took
the deterministic source-ambiguous rebase path and changed
`context_observer_generation`; the harness rejected that unallowed relation
change and cleaned up its exact disposable container.

The candidate adds only COORDINATOR to the existing outbox SELECT policy,
reseals the typed body, regenerates inert SQL, reproduces the exact PostgreSQL
catalogue, and hardens the behavior proof. It requires exact transaction-local
result markers for `BTR-E04`, `BTR-I03` and rollback scenario `BTR-B03`, and a
ninth independent `BTR-R03` connection proves the coordinator still lacks a
direct table `SELECT` grant.

Decide whether the repair restores only the entry point's required row
visibility and proves exact outcomes without creating direct read/write,
cross-practice, command, runtime or product authority. Prior receipts are
context, not acceptance; rerun the checks.

## Exact allowed surface

Review only AGENTS.md and these directly cited families:

- behavior plan/design/threat-model delta and the new outbox/result-marker
  parent-rebind document;
- failure/diagnosis evidence 038 and its exact diagnosis script/test;
- structural contract/schema/tests and outbox-select RLS repair;
- typed body contract/tests and body rebind;
- inert SQL, manifest, renderer and focused tests;
- parse contract/schema/harness/tests, immutable outbox characterization and
  exact reproduction evidence;
- behavior contract/schema/harness/tests;
- AER-0212 through AER-0214, register revision 185, pattern report and focused
  register tests; and
- the current Ariadne receipts and preflight named by this packet.

Do not inspect protected holdouts, historical Diary material, `docs/branding/`,
patient/clinical/product-derived data or unrelated paths. Do not use
repository-wide content search outside this allowlist.

## Required challenges

Verify and report:

1. exact clean HEAD before/after and exact baseline-to-candidate diff;
2. failure 038 SHA-256
   `68ebd0c6973c65048b8d1c73bc86573e4b6614587001b81b3ab2f396fd7f2f2d`,
   attempt `2171447fafa976485041ae03`, `BTR-E04`,
   `forbidden_relation_change`, changed relation
   `context_observer_generation`, `expected=20, observed=0, passed=0`, and
   exact cleanup absence;
3. diagnosis 038 SHA-256
   `109938d61c4c3e57ff5f13269e22b570c71350f61698353081a95bca1fda245b`
   proves forced-RLS outbox policy `pol_cf_03_select` omitted COORDINATOR while
   the transition function requires the exact source-position set;
4. the repaired policy admits exactly PRODUCER, OBSERVER, COORDINATOR and
   RETENTION with unchanged binding predicate, forced RLS and no direct grant;
5. coordinator direct table DML and SELECT grants remain empty, body-program
   semantics and function grants remain unchanged, and hostile tests reject
   policy or authority widening;
6. structural source `e1ca28915b09636e5d9d693216beef450f71a356`
   has canonical file digest
   `sha256:d333ad3ef75725a8a85e7d45a072bca02a087ea869d395459140c405919814c6`
   and sealed contract digest
   `sha256:30401808c97e45ad0ecf23242a21c1b7be35bc7d37343bb2f1ab4ef139e83a5f`;
7. body source `1a06961916bcf73d553eb401eb08094aa4c45e20`
   has canonical file digest
   `sha256:c88653b1db1e379e9d067dbe444a1c2cbdf0dd1dd148fe838bce274741f7c455`
   and sealed contract digest
   `sha256:9b079af00e46b5e18f464cc39f9283ce400ee7b2621d875a127af19cb908ee62`;
8. inert source `497a4d1fe5b58fa4bcc03747abb3d389c3b51899`
   is exactly 1,436,481 LF bytes, 423 statements and SHA-256
   `265ce41ec4c3b318cc42c544ab06ebb0fcc67904072b0f8406af4ec8ddec6b0a`;
   manifest SHA-256 is
   `559a66e508c2a38dbfc037d3e1df482cff7106dc09ff35001b55afc63b119cbf`;
9. immutable characterization evidence SHA-256 is
   `e053ac337a7b6db258b94bd56d0d55a0bd7c7ea42e428899bd566b154ba6c724`
   and changes only policies to count 47/digest
   `sha256:32f7416e38351c706d93ac235d8a1f19f4d67a3d691a86a17e8bb3032a72e4c0`;
10. immutable exact parse evidence SHA-256 is
    `b0ce639981a5822e9e66ebbb81cab74009b3ebe368f3d9e6efd75cfd32453386`,
    attempt `04deaadd7c685cbdd4d597c8`, all 17 digests match under contract
    `sha256:f74edcc816fb5794272352a482c1ae699f1dce822d301d86cb56ad6831cc2d8f`,
    rollback passes and exact container cleanup is proved;
11. behavior contract canonical digest is
    `sha256:4ca9f7612bd79159bc2232cec5bc078219ac2145c9d1ad80927420d2f8706f16`
    and binds exactly the six current parents;
12. scenario population/order remain twenty and category counts `6/4/3/4/3`;
    the intentional BTR-R03 evidence-strengthening changes the scenario-set
    digest to
    `d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`
    without adding a scenario or authority;
13. each of BTR-E04/I03/B03 invokes `apply_durability_transition_v1` once in a
    MATERIALIZED CTE and proves respectively `RECEIPT_APPLIED`,
    `RECEIPT_REPLAYED`, `RECEIPT_APPLIED`; missing, duplicate, malformed,
    mismatched, boolean or unexpected markers fail closed; B03 emits its marker
    before the fixed `P0001` rollback;
14. `ALLOWED_DIGEST_CHANGES["BTR-E04"]` does not include
    `context_observer_generation` and has no other widening;
15. BTR-R03 uses nine distinct fresh connections; its new
    `coordinator_outbox_direct_select` must fail `42501` despite the RLS policy
    because no direct table SELECT grant exists;
16. the evidence schema admits exact historical matrix generations 5 and 8
    plus current generation 9, while current deterministic tests require 9;
17. revision 185 contains 214 closed/contained incidents through AER-0214 and
    the register/pattern report remain exact;
18. protected mutable behavior evidence remains byte-identical at SHA-256
    `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`;
19. no Docker/runtime harness, credential, network, mount, port,
    application/API/Diary surface, watcher/listener/feed, product/patient data,
    provider, deployment, release, Pages or protected-ref boundary widened;
20. all tests below, Ruff and diff checks pass; and
21. candidate HEAD and checkout remain exact and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r166 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_038_outbox_rls_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_038_outbox_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_038_outbox_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
git diff --check 810a9dc11bdb39f76f70a6b65cb8afe10732e612..ede9bfad1a35f34c13148354af54881e5037ba3f
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, access patient/clinical/product
or protected data, inspect `docs/branding/`, move refs or accept your own
output.

Return `revision_required` for any P0-P2 finding, authority widening, parent or
scenario drift, test failure, dirty postcondition or incomplete packet.
Otherwise return exact `pass` with findings, commands/counts, exact HEAD and
cleanliness.
