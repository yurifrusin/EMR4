# Independent veto: BTR-E04 obligation readback scope recovery

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r168`
- Branch: `codex/review-context-fabric-obligation-scope-c8a3d2b`
- Diagnosed baseline: `c23c65a364a576b553ab0640cf4206c2d95f7e24`
- Candidate: `c8a3d2b51b8249ab7fee0a373c9dc8b2d375ecc3`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose and allowed surface

Independently verify failure 040, its static diagnosis and the exact readback
scope repair before any further disposable PostgreSQL run. Review only
AGENTS.md, diff `c23c65a..c8a3d2b`, immutable failure/diagnosis evidence 040,
their script/test/document, the behavior harness and focused test, AER-0216
with revision 187/register/pattern report, and the current receipt/preflight
packet. Prior review receipts are context, not acceptance.

Do not inspect the mutable behavior evidence alias, protected holdouts,
historical Diary material, `docs/branding/`, patient/clinical/product-derived
data or unrelated paths. Do not use repository-wide content search outside
this allowlist.

## Required challenges

Verify and report:

1. exact clean HEAD before/after and exact baseline-to-candidate diff;
2. failure 040 SHA-256
   `93af223dfb25aab6a217f98eea45aa43c27efdb2d85d102caaf0f3b05b41ff98`,
   attempt `75824e149eb55dfe398872e0`, BTR-E04 failed index `[5]`, stage
   `readback`, code `scenario_probe`, and exact container cleanup absence;
3. failed index 5 maps exactly to `one_pending_reassembly_obligation`;
4. diagnosed parent source is exact `c23c65a364a576b553ab0640cf4206c2d95f7e24`
   with harness SHA-256
   `6898425497bb1361b096932bedc9f637ad5b381434100a45df11e6ac227d9928`;
5. the bootstrap deliberately seeds one beta pending obligation using the same
   authored-synthetic happy observer identifier;
6. BTR-E04 passed its transition result and relation-delta gate before the
   probe, including exactly one newly added obligation;
7. the parent BTR-E04 obligation predicate filtered only observer plus state,
   omitted practice/stream and therefore matched the beta preseed plus alpha
   result; BTR-I03 contained the same scope omission;
8. diagnosis generated zero additional container/database runs and persisted
   no raw PostgreSQL values;
9. the correction adds exact alpha practice and stream only to the BTR-E04 and
   BTR-I03 obligation probes, with a hostile test retaining the beta preseed;
10. database artifact, body, behavior contract, scenario population/order,
    expected deltas, allowed digest changes and authority grants are unchanged;
11. revision 187 contains exactly 216 corrected/contained incidents through
    AER-0216 and prior incidents are unchanged;
12. the protected mutable evidence alias is deliberately absent from the
    committed review surface;
13. no Docker/runtime harness, credential, network, application/API/Diary,
    patient/clinical/product data, provider, deployment, release, Pages or
    protected-ref boundary opens;
14. all checks below pass; and
15. candidate HEAD and checkout remain exact and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r168 tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py scripts\raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_039_probe_index_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
git diff --check c23c65a364a576b553ab0640cf4206c2d95f7e24..c8a3d2b51b8249ab7fee0a373c9dc8b2d375ecc3
git status --short --branch
git rev-parse HEAD
```

Do not edit, commit, push, start Docker/PostgreSQL, run a runtime harness,
contact providers/products, inspect forbidden data, move refs or self-accept.
Return `revision_required` for any P0-P2 finding, drift, failed check, dirty
postcondition or incomplete evidence; otherwise return exact `pass`.
