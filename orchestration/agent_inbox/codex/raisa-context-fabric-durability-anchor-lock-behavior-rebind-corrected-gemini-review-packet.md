# Corrected independent veto: recovery-anchor lock visibility

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r162`
- Branch: `codex/review-context-fabric-anchor-lock-portable-040a069b`
- Baseline: `978f54205966d412a9a5ead03b1c2c16ca46c5e0`
- Rejected predecessor: `263c1ca833dfdc53d5db32c6d57caeadb1edd20d`
- Candidate: `040a069b4b6496b84ba402c2407a44e47aa39a02`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose and first-review disposition

The first exact r161 Gemini 3.6 Flash/high veto passed every substantive
anchor-lock, parent, evidence, containment and scenario challenge, but correctly
returned `revision_required` because one required diagnosis test depended on
intentionally untracked mutable evidence absent from a clean worktree. That
receipt is preserved at
`orchestration/agent_inbox/antigravity/raisa-context-fabric-durability-anchor-lock-behavior-rebind-review-receipt.json`.

Independently verify the complete baseline-to-candidate repair and decide
whether descendant `040a069b...` fixes that evidence-portability defect without
altering the accepted database or behavior semantics. Prior prose is context,
not acceptance; rerun all required checks.

## Allowed surface

Review only the exact diff and directly cited files:

- structural contract/schema and exact policy tests;
- typed body contract, inert SQL and manifest;
- parse contract and immutable anchor-lock characterization/reproduction;
- behavior contract, harness and tests;
- failure/diagnosis evidence 036 and diagnosis script/test;
- tracked immutable diagnosis 029;
- the three anchor-lock recovery/rebind documents and threat-model delta;
- AER-0202 through AER-0206, revision 178 and pattern report;
- first review packet/receipt and current Ariadne receipts.

Do not inspect any protected holdout, historical Diary, branding,
patient/product-derived or unrelated path. Do not use repository-wide content
search outside this allowlist.

## Required challenges

Verify and report:

1. exact clean HEAD before/after and exact baseline-to-candidate diff;
2. failure 036 SHA-256
   `662022a5d0d3744a91397b6a6b8d89e0bfc488631e88691053a7536d914de75c`,
   attempt `701e15b874bd1c79f95466b5`, `BTR-E04`, `CF004`, function line
   299, fail-closed evidence reconciliation `expected=20, observed=0, passed=0`
   and exact cleanup;
3. diagnosis 036 SHA-256
   `430de45959a852a146e4f3bb8f88c2ee5fdd1ce193b8d9b833440df9fd91c63b`
   correctly proves one plain-visible anchor became invisible only to
   `FOR SHARE` under forced RLS;
4. `pol_cf_08_update_lock` is permissive `FOR UPDATE TO PUBLIC`; USING binds
   only exact practice/stream COORDINATOR or LIFECYCLE capability; WITH CHECK
   repeats that predicate plus `AND FALSE`; both roles retain zero direct DML,
   and no entry-point, typed-body or command authority widens;
5. hostile structural tests reject missing/widened/foreign/non-PUBLIC policy
   forms, while BTR-R03 denies direct anchor UPDATE for both roles on separate
   fresh connections;
6. body program semantics and twenty scenario objects/order are unchanged;
   scenario counts remain `6/4/3/4/3`, scenario population digest remains
   `7c8709c2ec1c0eb69da86fe037f551355ada6c1294e2ca4f2ce7f15ad89be5b3`;
7. structural digest is `6802a735...`, sealed body digest is `b54b2e68...`,
   inert SQL is 1,435,884 LF bytes / 422 statements / SHA-256 `550336e1...`,
   and manifest SHA-256 is `95a5c0a6...`;
8. characterization evidence SHA-256 is `e1568e12...`, only the policies
   digest changed from the preceding generation, and count is 46;
9. exact parse reproduction SHA-256 is `28be342c...`, matches all 15 bound
   digests under contract `ce968bac...`, proves rollback and exact cleanup;
10. behavior contract binds all six parents at canonical SHA-256 `ade8a499...`;
11. descendant change from `263c1ca8` to `040a069b` does not touch structural,
    body, inert, parse or behavior contract semantics; it replaces only the
    untracked mutable-path test dependency with tracked immutable diagnosis 029;
12. diagnosis 029 has exact file SHA-256
    `1e5c22aa6098acfa0764161af4f1f27c292fa249faac96aa699a20aa1f700214`
    and anchors the protected mutable evidence at SHA-256
    `09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`
    and attempt `fce9773c076f3ede41a4875c`; no test requires the untracked path;
13. AER-0206/revision 178 accurately records the rejected review and repair,
    the register has 206 closed incidents, and the pattern report is exact;
14. no Docker runtime, credential, network, mount, port, data, product,
    deployment, release, Pages or protected-ref boundary widened;
15. all tests below, Ruff and diff checks pass; and
16. candidate HEAD and checkout remain exact and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r162 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_036_anchor_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 978f54205966d412a9a5ead03b1c2c16ca46c5e0..040a069b4b6496b84ba402c2407a44e47aa39a02
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

Return `fail` for any P0-P2 finding, missing immutable evidence, untracked-path
dependency, policy/authority widening, parent/scenario drift, test failure,
dirty postcondition or incomplete packet. Otherwise return exact `pass` with
findings, commands/counts, HEAD and cleanliness.
