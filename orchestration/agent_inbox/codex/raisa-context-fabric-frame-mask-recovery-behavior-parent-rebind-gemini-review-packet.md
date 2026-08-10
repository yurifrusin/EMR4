# Independent veto: frame-mask recovery behavior-parent rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r175`
- Branch: `codex/review-context-fabric-behavior-frame-mask-rebind-ddec7525`
- Candidate: `ddec752578b39b708b76f0bfa75953fce14607fa`
- Immediate predecessor: `9bf59ed860e2c4e119b13e5dd38911dbb9591ad0`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md; exact diff `9bf59ed8..ddec7525`; the committed immutable
frame-mask parse/catalogue pass and its acceptance document/test; the behavior
contract, harness and two behavior test files; the behavior-parent rebind
document and orchestrator receipt; and the inert SQL/render manifest only as
needed to resolve the declared canonical bindings. Do not inspect the mutable
behavior evidence alias, protected holdouts, historical Diary data,
`docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before/after, exact branch/diff and protected refs;
2. immutable accepted runtime source has raw/canonical SHA-256
   `4583c8b0bca881964ba9a337cfd1b5c9ae535ad7cc78c06766f844ffe95d998a`,
   attempt `9e006c12fcdea5844c2fe4ad`, pass result, all catalogue digests matched and
   complete cleanup;
3. `accepted_runtime_source` resolves byte-exactly from source head
   `9bf59ed860e2c4e119b13e5dd38911dbb9591ad0`;
4. inert SQL and render manifest resolve byte-exactly from
   `a8cef7045fcada54a33a1060e83fd4d9929ac56b` at canonical SHA-256
   `fc1c00ab7209a6689f4de29a14a134719a0110dfd3b556172781384332af41fa`
   and `fec0bb1399ebf5af0d06ca933069614ca4a8c84a9593d5eee0e983b0afffb9fd`;
5. structural, body and prerequisite bindings remain byte-for-byte unchanged;
6. canonical behavior contract SHA-256 is
   `9dd97600289733fb48a03a54d0b4a2418c6c502c98f75ba0181213a6088518dc`;
7. all 20 scenarios, their order, fixtures, principals, roles, capabilities,
   RLS, expected SQLSTATEs, transaction shapes and command boundaries are
   unchanged;
8. the harness remains fail-closed on canonical contract and source-head
   binding drift;
9. the immutable attempt-045 failure remains historical and no attempt 046 or
   later behavior result is claimed;
10. all exact checks below pass with a clean postcondition; and
11. no Docker/PostgreSQL run, operational database, watcher/feed,
    application/API/Diary wiring, provider/product data, deployment, Pages or
    protected-ref boundary opens.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r175 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_ariadne_orchestrator_preflight.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
git diff --check 9bf59ed860e2c4e119b13e5dd38911dbb9591ad0..ddec752578b39b708b76f0bfa75953fce14607fa
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run either disposable
database harness, contact another provider/product, inspect forbidden data,
move refs or self-accept. Return `revision_required` for any P0-P2 finding,
drift, failed check or dirty postcondition; otherwise return exact `pass`.
