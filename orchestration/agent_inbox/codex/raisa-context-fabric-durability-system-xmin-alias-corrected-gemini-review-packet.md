# Corrected independent veto packet: durability system-xmin explicit-alias recovery

Date: 2026-08-09

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r104`
- Branch: `codex/review-context-fabric-system-xmin-alias-7727d1c`
- Baseline: `e9fcbe4a7f1a85c71ce164a88c639e2a8910d18c`
- Candidate: `7727d1c61426a846a6b68bc7d855733c45aef78b`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete five-source rehydration required by `AGENTS.md` and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose and prior rejection

Independently decide whether the complete explicit-`xmin`-alias recovery is
eligible for exactly one contained behavior rehearsal. The first review at
`e8d897c` has no acceptance authority: its packet mistyped three full exact
identifiers and its verifier returned `pass` despite reporting contradictory
candidate values. AER-0144/AER-0145 and the rejection receipt preserve that
failure. This distinct fresh review must use the corrected values below.

## Allowed surface

Review only the exact baseline-to-candidate diff and changed paths plus their
directly cited contracts, schemas and tests: the explicit-alias recovery,
parse/behavior rebind and threat documents; AER revisions 120-121; attempt-020,
diagnosis, characterization and parse evidence; inert SQL/render manifest;
typed structural/body, parse, behavior and prerequisite contracts; the three
harnesses and eight exact test files below; and the first-review rejection
packet/receipt/reconciliation. Do not search or enumerate any protected
holdout, historical Diary, branding, patient, product-derived or unrelated
path.

## Corrected exact values and required challenges

Verify and report all of the following:

1. exact candidate HEAD, diff and clean checkout before and after review;
2. failed behavior attempt 020 validates at file SHA-256
   `a07e340ad9383cceb2a48f2c8230829daace833711b6d442af513022a767f8ac`,
   records BTR-E01/SQLSTATE 42703, zero scenarios and exact cleanup;
3. the no-raw-error diagnosis maps `cf_fence_stream_head_v1` line 33 to record
   `final_head` and unavailable field `xmin`, with diagnosis-container cleanup;
4. renderer 2.0.8 emits `relation.xmin AS xmin` at all 62 affected exact-read
   sites, leaves zero unaliased `.xmin INTO STRICT` forms and rejects an
   authored unaliased mutation;
5. inert SQL remains 412 statements and exactly 1,403,680 LF bytes at SHA-256
   `45c90b927a6e5a9b5b367ddf6ca76dfde0491ddb04d74214383cbca68419b7f6`;
6. render-manifest raw/canonical SHA-256 is
   `8893d0a21ce004bf5b57ad89deec75b8f4ae9a6a2f9705f9c6e6d598ec2da164`,
   body semantic SHA-256 remains
   `8ede994ba6f9bbeade0eb015bb9dd23dade21934e7c70fa6885a4a67654aab18`,
   and the corrected full structural contract SHA-256 is
   `d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6`;
7. characterization evidence file SHA-256 is
   `e77af8076d37fa4690a829ece3ecd7b3c3d8a4392285c89ffbc5a2044044ddfa`
   and the corrected full cleanup container ID is
   `e10340911ad8afef2f33da41319a1b52994584c2fc958c40b9c7219f5055c63e`;
8. exact parse evidence file SHA-256 is
   `67ef8251ed08ed8f17bf86e44c8f4f6ad1e74fad51eeca553adb2b641e0d8915`,
   contract SHA-256 is
   `d89dbc031649fdbe11eba5a1290c0d117e8b4958f884b74bd1e13c05c6eb30de`,
   all frozen catalogue proofs match, and the corrected full cleanup container
   ID is
   `253f1b17c19af1a898ea3f593293865bacd1fd474686703b77acbb42ae3c3af8`;
9. behavior contract canonical SHA-256 is
   `58e8508bf41c5d343b0738dcb4a446f94db8f90e6df9fb7ff5d7d9a2291612df`,
   all twenty scenario objects/order remain identical at digest
   `7c8709c2966814c123ad4312cfeb2296f1bdcbe9c05bd0826882917371346820`
   and category counts `6/4/3/4/3`, with only parent bindings changed;
10. AER revision 121 validates with 145 incidents and zero open; AER-0144
    records the first packet's three full-identifier mistakes, AER-0145 records
    the inadmissible terminal pass, and neither incident claims more than the
    observed process failures;
11. the first receipt SHA-256 is
    `6a485769d62821b27d6d357d177ad75338eb8a1ff7227f82b2485a9241fd2843`,
    its `pass` is explicitly rejected, the candidate was unchanged and no
    runtime was admitted;
12. the mutable current behavior evidence remains failed attempt 020 and is not
    treated as accepted or staged;
13. no Docker, credential, network, mount, port, data, provider, product,
    deployment, release, Pages or protected-ref boundary widened;
14. the exact eight-file command below passes 394 tests, Ruff and diff checks;
15. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r104 tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check e9fcbe4a7f1a85c71ce164a88c639e2a8910d18c..7727d1c61426a846a6b68bc7d855733c45aef78b
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, inspect `docs/branding/`, access
patient/clinical/product/protected data, move refs or accept your own output.

Return `fail` for any P0-P2 finding; any mismatch in a full identifier above;
any remaining unaliased affected system-`xmin`; typed/scenario drift;
inadmissible first-review acceptance; widened containment; incomplete 394-test
packet; or dirty postcondition. Otherwise return one exact `pass` with the
verified values, command results, HEAD and cleanliness.
