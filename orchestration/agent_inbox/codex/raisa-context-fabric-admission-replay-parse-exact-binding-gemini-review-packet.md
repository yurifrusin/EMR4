# Independent veto: admission-replay exact catalogue binding

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

Review clean worktree
`C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-parse-r178`
on branch `codex/review-context-fabric-admission-replay-parse-exact-e5912ea4`
at exact candidate `e5912ea490c35772a142a40e0ff9030de492f8ac`, predecessor
`d5f49d4061c80af4696ec1a975148b3e634b7805`. Protected refs remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration naming all five required
sources. Review only AGENTS.md; exact diff
`d5f49d4061c80af4696ec1a975148b3e634b7805..e5912ea490c35772a142a40e0ff9030de492f8ac`;
the immutable admission-replay characterization evidence, parse contract and
harness/tests, bounded rebind note and run receipts. Do not inspect mutable
evidence aliases, holdouts, historical Diary data, `docs/branding/`,
patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate and protected refs before/after;
2. exactly one characterization attempt `50991d94ce26e0a074dbbfd1` is preserved
   at immutable SHA-256
   `f1320a45b3c604315f04985e36221bfaa5ddfe5788ace621b7d1566706b4b29a`;
3. it returned only `catalogue_characterization_required`, matched atomic
   rollback, parsed exact artifact SHA-256
   `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`
   and completed exact-ID cleanup;
4. all 15 acceptance-bound digests and object counts equal the preceding
   accepted catalogue; this is consistent with a function-body-only change
   because artifact SHA and parse admission bind the body while catalogue
   queries bind external signature/security shape;
5. exact-bound contract canonical SHA-256 is
   `b891ab30e5173475b8e15ead861013b2e4b209575a66ce0028a5c3ad974107f6`;
6. no result is yet claimed as exact reproduction or behavior proof;
7. all commands below pass and postcondition stays clean; and
8. no database run, operational database, watcher/feed, application/API/Diary
   wiring, provider/product data, deployment, Pages or protected refs open.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r178 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
git diff --check d5f49d4061c80af4696ec1a975148b3e634b7805..e5912ea490c35772a142a40e0ff9030de492f8ac
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
