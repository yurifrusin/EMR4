# Independent veto packet: durability system-`xmin` repair and behavior rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r102`
- Branch: `codex/review-context-fabric-system-xmin-971c251`
- Baseline: `ae5b33c1e5d1f9b12d6f10cefb1c9e577e72189c`
- Candidate: `971c251903ea30ed0b62361062a7a76fdc54ba3f`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently decide whether attempt 019 correctly exposed use of PostgreSQL's
system `xmin` through a named table-composite local, whether the typed-body
repair covers every such local use without semantic widening, whether the
regenerated artifact passed exact parse/catalogue proof, and whether the
unchanged twenty-scenario behavior contract is rebound only to accepted
parents.

## Allowed review surface

Review the exact baseline-to-candidate diff and only its changed files plus
directly imported/cited contracts, schemas and evidence. The relevant surface
is:

- the system-`xmin` diagnosis/recovery, threat delta, parse rebind/accepted
  source and behavior-rebind documents;
- AER revision 119, AER-0142, the register and generated pattern report;
- behavior failure 019, diagnosis 019a and its diagnosis receipt;
- body contract/program catalogue/validator, inert SQL/manifest/renderer,
  parse contract/harness/evidence and behavior contract/harness;
- the exact focused tests named below; and
- exact Ariadne provenance files in the candidate diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not run a
repository-wide content search outside this packet.

## Required challenges

Verify and report:

1. exact candidate HEAD, baseline-to-candidate diff and clean checkout before
   and after review;
2. attempt-019 failure evidence has file SHA-256
   `57784ad383ff8eef4f3b8439af324585bebf1ee93856a247e328423ae05e8ced`,
   records `BTR-E01`, SQLSTATE `42703`, zero scenarios and exact cleanup;
3. immutable diagnosis 019a has file SHA-256
   `ef164d9713e8e8d55433a1d01eb95452d8f4c8e40e4fbef286589210db3162fb`,
   retained no raw error, and the bounded coordinate is function
   `emr4_context_fabric.cf_fence_stream_head_v1`, line 33, relation composite
   `emr4_context_fabric.context_observation_stream_head`, column `xmin`;
4. the root cause is sound: a named table composite carries user columns, not
   PostgreSQL system columns; the typed repair explicitly adds `xmin` to all
   three shared exact projection catalogues (alias, stream head, outbox),
   renders all fourteen affected locals as `record`, and the validator rejects
   `SYSTEM_XMIN` unless the definitely assigned exact read projected `xmin`;
5. body semantic SHA-256 is
   `8ede994ba6f9bbeade0eb015bb9dd23dade21934e7c70fa6885a4a67654aab18`;
   structural contract is unchanged; statement count remains 412; regenerated
   SQL is exactly 1,403,184 LF bytes at SHA-256
   `0379b35fe34eb5cc7f78a45d55a54b3b429e5f85af591e1c5bdf4080e3a15c7c`;
6. AER-0142 and revision 119 coherently record the repository defect and
   prevention control, with 142 incidents and zero non-corrected incidents,
   without unsupported model/provider causation;
7. bounded catalogue characterization has file SHA-256
   `a34da84879a7d761bf5365acd9df76da46c296c37d740288ddbe029add9f15b6`,
   cannot pass, reproduces the complete unchanged digest set and proves exact
   cleanup;
8. exact parse evidence has file SHA-256
   `b3eab7e0e79a87493750b5b825d452f826d37377e4a7cf5b747a563f6ec57718`,
   proves expected `42601` rollback, matches all 17 frozen catalogue digests,
   binds the exact corrected artifact and proves cleanup/absence of container
   `3ff747993c6f9df9902468ad43a80a02ad7a16ef4237e30385295bad9028165d`;
9. behavior contract changes only six parent-binding values/paths needed for
   the accepted parse ledger, inert SQL/manifest, body contract and unchanged
   prerequisite source; all twenty scenario objects and order are identical to
   baseline with scenario digest
   `7c8709c2ec1c0eb69da86fe037f551355ada6c1294e2ca4f2ce7f15ad89be5b3`,
   category counts `6/4/3/4/3`, and canonical behavior SHA-256
   `b8855abe3bdb7b63394d1889a7dd49eb1d08484d49c722fc1dc4e4bec5097ad2`;
10. the registry-barrier fixture remains exactly one alpha row at revision
    zero and `BTR-E01` still expects zero row delta and exact revision three;
11. no Docker, credential, network, mount, port, data, provider, product,
    application runtime, migration application, deployment, release, Pages or
    protected-ref boundary widened;
12. all 390 focused tests, Ruff and diff checks pass; and
13. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r102 tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check ae5b33c1e5d1f9b12d6f10cefb1c9e577e72189c..971c251903ea30ed0b62361062a7a76fdc54ba3f
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run either runtime
harness, contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong evidence hash/coordinate, incomplete
`xmin` projection/validation coverage, typed semantic or scenario drift, parse
evidence mismatch, widened containment, incomplete deterministic packet or
dirty postcondition. Otherwise return one exact `pass`, stating findings,
commands/counts, HEAD and post-review cleanliness.
