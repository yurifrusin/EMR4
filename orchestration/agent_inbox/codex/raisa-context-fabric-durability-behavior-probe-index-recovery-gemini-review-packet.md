# Independent veto: failure-039 diagnosis and bounded probe-index evidence

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r167`
- Branch: `codex/review-context-fabric-behavior-probe-index-c23c65a`
- Baseline: `ede9bfad1a35f34c13148354af54881e5037ba3f`
- Candidate: `c23c65a364a576b553ab0640cf4206c2d95f7e24`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently verify the failure-039 evidence and the diagnostic-only recovery
before any further disposable PostgreSQL run. Attempt 039 admitted BTR-E04's
exact `RECEIPT_APPLIED` transition marker and its allowed relation delta, then
failed one of seven value-free semantic predicates. The rejected evidence
persisted only a digest that deterministically identifies BTR-E04, not the
failed predicate index.

The candidate preserves that failure immutably, proves exact cleanup and zero
additional database runs during diagnosis, and adds a bounded locator to future
failure evidence. Probe results must be an exact boolean array of the expected
scenario-specific length. Only unique one-based failed indexes from 1 through
16 may be persisted; no raw PostgreSQL values may be released. The database
artifact, typed behavior contract, twenty scenarios, allowed relation changes,
provider boundary and product boundary must remain unchanged.

## Exact allowed surface

Review only AGENTS.md and these cited families:

- commit diff `ede9bfa..c23c65a`;
- immutable failure 039, its deterministic diagnosis evidence, diagnosis
  document, script and focused test;
- behavior evidence schema, behavior harness and its focused tests;
- AER-0215, register revision 186, pattern report and focused register tests;
- the committed prior result-marker review and attempt-039 preexecution
  provenance; and
- this packet, its preflight and dispatch receipt.

Do not inspect the mutable behavior evidence alias, protected holdouts,
historical Diary material, `docs/branding/`, patient/clinical/product-derived
data or unrelated paths. Do not use repository-wide content search outside
this allowlist.

## Required challenges

Verify and report:

1. exact clean HEAD before/after and exact baseline-to-candidate diff;
2. immutable failure 039 SHA-256
   `4e0d7142187e64aa4516d115d444236b3b67582ef7a239bc37c00b00e0038f27`,
   attempt `5dcf0e6427694521e3a2ca26`, run sequence 39, stage `readback`,
   code `scenario_probe`, expected scenario count 20, observed/passed 0, and
   exact owned-container cleanup absence;
3. the persisted detail digest maps exactly and only to `BTR-E04` and the
   diagnosis evidence SHA-256 is
   `c0cc4f2dd3bb1126fa3543f858b466d7f9d866d556e2eee388745c17486b9955`;
4. control flow proves `RECEIPT_APPLIED` and allowed relation-delta admission
   occurred before the BTR-E04 semantic probe, without claiming which of its
   seven predicates failed;
5. diagnosis generated no database/container run, releases no raw database
   value and proves the original owned container absent;
6. `EXPECTED_PROBE_COUNTS` covers exactly the ten multi-item probe scenarios
   with counts E01=6, E02=7, E03=3, I01=2, E04=7, I03=2, E05=2, I02=3,
   R03=2 and B03=2;
7. `_probe` requires an exact object containing only `checks`, an exact list
   length, and exact booleans (not integer truthiness); malformed material
   fails closed as `scenario_probe_shape`;
8. false entries produce only the scenario ID plus unique one-based failed
   indexes, with no probe values or database rows;
9. evidence admission copies `failed_probe_indexes` only when it is a list of
   1 through 16 unique exact integers, excluding booleans and values outside
   1 through 16;
10. the evidence schema makes this field optional for historical failures but,
    when present, enforces the same array length, uniqueness and integer bounds;
11. hostile tests cover missing/wrong shape, non-boolean checks, multiple
    failed indexes, 0, 17, duplicate, boolean and overlong arrays;
12. database artifact, behavior contract, scenario population/order,
    `ALLOWED_DIGEST_CHANGES`, transition SQL and authority grants are unchanged
    from baseline;
13. the protected mutable evidence alias is deliberately absent from this
    committed review surface and no code attempts to inspect, stage or rewrite
    it;
14. AER-0215 records the harness evidence gap without rewriting AER-0001
    through AER-0214; revision 186 has exactly 215 corrected/contained
    incidents and its exact counts/pattern report pass;
15. no Docker/runtime harness, credential, network, mount, port,
    application/API/Diary surface, watcher/listener/feed, product/patient data,
    provider, deployment, release, Pages or protected-ref boundary widened;
16. all checks below pass; and
17. candidate HEAD and checkout remain exact and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r167 tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
git diff --check ede9bfad1a35f34c13148354af54881e5037ba3f..c23c65a364a576b553ab0640cf4206c2d95f7e24
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, access patient/clinical/product
or protected data, inspect `docs/branding/`, move refs or accept your own
output.

Return `revision_required` for any P0-P2 finding, authority widening, contract
or scenario drift, test failure, dirty postcondition or incomplete packet.
Otherwise return exact `pass` with findings, commands/counts, exact HEAD and
cleanliness.
