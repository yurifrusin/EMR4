# Independent veto: admission-replay behavior parent rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

Review clean worktree
`C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r179`
at exact `116fcca713f804e8234e60b3cdff9ebac567f50d`, predecessor
`36f076775e676620f99650043b05bd852e3a84be`. Protected refs remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform complete five-source AGENTS.md rehydration. Review only AGENTS.md;
exact diff `36f076775e676620f99650043b05bd852e3a84be..116fcca713f804e8234e60b3cdff9ebac567f50d`;
the behavior contract/harness/test and bounded parent-rebind note; plus tracked
immutable parse evidence and exact generated parent files needed to reconcile
their hashes. Do not inspect mutable evidence aliases, holdouts, historical
Diary data, `docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate and protected refs before/after;
2. accepted runtime parent is immutable parse reproduction SHA-256
   `9ad82882150f8795789c332db8bed6e4b50d150986a6066ce832f12e48246d24`
   at source `36f076775e676620f99650043b05bd852e3a84be`;
3. inert SQL and manifest are exact SHA-256
   `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
   and `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`
   at source `5a9a7ae907308aa0a8a4256e9043b833f8c416ae`;
4. canonical behavior contract is
   `43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615`;
5. scenario order, fixtures, outcomes, SQLSTATEs, category counts `6/4/3/4/3`,
   containment and claim boundaries are unchanged; BTR-I02 retains its three
   transaction replay proof;
6. all commands below pass cleanly; and
7. no Docker/PostgreSQL run, operational database, watcher/feed,
   application/API/Diary wiring, provider/product data, deployment, Pages or
   protected refs open.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r179 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py
git diff --check 36f076775e676620f99650043b05bd852e3a84be..116fcca713f804e8234e60b3cdff9ebac567f50d
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
