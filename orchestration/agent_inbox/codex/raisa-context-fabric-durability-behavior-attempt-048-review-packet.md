# Independent final evidence veto: Context Fabric behavior attempt 048

Date: 2026-08-08

Decision required: exactly one schema-constrained `pass` or
`revision_required`.

Review clean short worktree `C:\Users\sarashera\EMR4-worktrees\r182` at
exact `f3383dc4099b4ee590014bea62dddb146f5d2a16`, predecessor
`0151686d0eb01a37169c554f9eb5b2bac63ccda6`. Protected refs remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform complete five-source AGENTS.md rehydration. Review only AGENTS.md;
exact diff `0151686d0eb01a37169c554f9eb5b2bac63ccda6..f3383dc4099b4ee590014bea62dddb146f5d2a16`;
the immutable attempt-048 pass, its evidence schema and exact test; the behavior
contract/harness/test; AER-0238 and register outputs; accepted parent evidence;
and exact generated artifact files needed to reconcile hashes. Do not inspect
mutable evidence aliases, holdouts, historical Diary data, `docs/branding/`,
patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate and protected refs before/after;
2. immutable pass SHA-256
   `26c6dec802e46dec055c1c42aecc97df9942180014fc9fa410f96e1305798200`,
   attempt `3ef353ae4f6648e3c9d36404`, result exact pass, 20 expected/observed/passed,
   exact contract order and category counts `6/4/3/4/3`;
3. lifecycle reaches `catalogue_reconciled_after_behavior`,
   `cleanup_verified`, `passed`, and exact container
   `4bbb33f427d5b006aecc38e6a1901c61d5581a69ed825b24d6266948b26702a6`
   is recorded removed and absent;
4. BTR-I02 proves three separate cross-transaction idempotent replay reads;
   BTR-B03 observes `RECEIPT_APPLIED`, then fixed `P0001`, with every rollback
   readback true including retained precommitted primary and absent receipt;
5. parent behavior contract, inert SQL and manifest are exact SHA-256
   `43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`,
   `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
   and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`;
6. the immutable pass validates whole-document against its schema; the nested
   stderr digest now reuses the repository's prefixed digest definition and a
   bare digest is rejected; no immutable evidence was rewritten;
7. AER-0238 and revision 204 truthfully record the repository schema defect and
   bounded correction; the pattern report is deterministic with 238 closed
   incidents;
8. all commands below pass cleanly; and
9. no Docker/PostgreSQL run, operational database, watcher/feed,
   application/API/Diary wiring, provider/product data, deployment, Pages or
   protected refs open.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r182 tests\test_raisa_context_fabric_durability_behavior_attempt_048_pass.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check tests\test_raisa_context_fabric_durability_behavior_attempt_048_pass.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check tests\test_raisa_context_fabric_durability_behavior_attempt_048_pass.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_047_rollback_gap_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check 0151686d0eb01a37169c554f9eb5b2bac63ccda6..f3383dc4099b4ee590014bea62dddb146f5d2a16
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run either database harness,
contact another provider/product, inspect forbidden data, move refs or
self-accept. Return `revision_required` for any P0-P2 finding, drift, failed
check or dirty postcondition; otherwise return exact `pass`.
