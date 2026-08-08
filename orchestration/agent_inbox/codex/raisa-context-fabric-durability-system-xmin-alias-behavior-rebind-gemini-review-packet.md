# Independent veto packet: durability system-xmin explicit-alias recovery and behavior rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r103`
- Branch: `codex/review-context-fabric-system-xmin-alias-e8d897c`
- Baseline: `e9fcbe4a7f1a85c71ce164a88c639e2a8910d18c`
- Candidate: `e8d897ce4bbc25874e0d9dc8b94c7bdc693e7f91`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether behavior attempt 020 correctly reconfirmed the
bounded PostgreSQL composite-record failure at `cf_fence_stream_head_v1` line
33, whether the diagnosis safely isolated the missing output alias on system
column `xmin`, whether renderer 2.0.8 repairs every affected exact-read
projection without semantic widening, whether exact parse/catalogue proof
passed, and whether the unchanged twenty-scenario behavior contract was
rebound only to accepted corrected parents.

## Allowed review surface

Review the exact baseline-to-candidate diff and only the changed files plus
their directly imported/cited contracts, evidence schemas and these canonical
parents:

- the system-xmin explicit-alias recovery, parse rebind, behavior rebind,
  threat-model delta and AER revision 120 documents in `docs/`;
- AER-0142/AER-0143, the generated error register and pattern report;
- behavior failure evidence 020, the bounded diagnosis receipt,
  characterization evidence and current exact parse/catalogue pass evidence;
- inert SQL, render manifest, behavior contract, structural contract, typed
  body contract and synthetic prerequisite contract;
- the inert renderer, parse harness and behavior harness;
- their exact tests named below; and
- exact Ariadne provenance files in the baseline-to-candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not use a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. attempt-020 evidence validates, has file SHA-256
   `a07e340ad9383cceb2a48f2c8230829daace833711b6d442af513022a767f8ac`,
   records `BTR-E01`, SQLSTATE `42703`, zero scenarios and verified exact
   cleanup;
3. the diagnosis receipt maps the same bounded coordinate to
   `emr4_context_fabric.cf_fence_stream_head_v1`, internal function line 33,
   record `final_head`, and the unavailable `xmin` field; it persists no raw
   database error and proves exact diagnosis-container cleanup;
4. renderer 2.0.8 changes each affected system-column projection to an
   explicit `relation.xmin AS xmin` output alias, every one of the 62 accepted
   exact-read occurrences is explicitly aliased, zero unaliased system-xmin
   projections and zero `.xmin INTO STRICT` forms remain, and an authored
   unaliased mutation is rejected artifact-wide;
5. the typed structural and function-body contracts remain semantically
   unchanged; statement count remains 412; the corrected SQL is exactly
   1,403,680 LF bytes at SHA-256
   `45c90b927a6e5a9b5b367ddf6ca76dfde0491ddb04d74214383cbca68419b7f6`;
   raw/canonical render-manifest SHA is
   `8893d0a21ce004bf5b57ad89deec75b8f4ae9a6a2f9705f9c6e6d598ec2da164`,
   body semantic SHA remains
   `8ede994ba6f9bbeade0eb015bb9dd23dade21934e7c70fa6885a4a67654aab18`,
   and structural SHA remains
   `d481b9913e5ce0889bb57224076b31764c2e0e0e93f22508a3533a5404db6bbd`;
6. AER-0143 coherently records the explicit-alias defect, register revision 120
   contains 143 incidents and zero open incidents, and no unsupported
   cross-attempt causal relationship is encoded;
7. characterization-only evidence has file SHA-256
   `e77af8076d37fa4690a829ece3ecd7b3c3d8a4392285c89ffbc5a2044044ddfa`
   and exact cleanup for container
   `e1034091c7b044bc79ceecedeb16513398039a6bfeb09e96c4740f10d114807e`;
8. exact parse evidence has file SHA-256
   `67ef8251ed08ed8f17bf86e44c8f4f6ad1e74fad51eeca553adb2b641e0d8915`,
   contract SHA-256
   `d89dbc031649fdbe11eba5a1290c0d117e8b4958f884b74bd1e13c05c6eb30de`,
   matches all frozen catalogue proofs, binds the exact corrected parent, and
   proves exact cleanup/absence of container
   `253f1b17bda2d0cabdc8bf12770c9c3d7832e4fa573b3972001351f9dac53d57`;
9. the behavior contract changes only accepted parent bindings, all twenty
   scenario objects and order are identical to the reviewed baseline with
   scenario digest
   `7c8709c2966814c123ad4312cfeb2296f1bdcbe9c05bd0826882917371346820`
   and category counts `6/4/3/4/3`, and its canonical SHA-256 is
   `58e8508bf41c5d343b0738dcb4a446f94db8f90e6df9fb7ff5d7d9a2291612df`;
10. the mutable current behavior evidence remains the failed attempt-020
    evidence and is neither treated as accepted nor staged by this review;
11. no Docker, credential, network, mount, port, data, provider, product,
    deployment, release, Pages or protected-ref boundary widened;
12. all 392 focused tests, Ruff and diff checks pass; and
13. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r103 tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check e9fcbe4a7f1a85c71ce164a88c639e2a8910d18c..e8d897ce4bbc25874e0d9dc8b94c7bdc693e7f91
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong evidence hash/coordinate, remaining
unaliased affected system-xmin projection, typed-contract/scenario drift,
parse-evidence mismatch, widened containment, incomplete deterministic packet
or dirty postcondition. Otherwise return one exact `pass`, stating findings,
commands/counts, HEAD and post-review cleanliness.
