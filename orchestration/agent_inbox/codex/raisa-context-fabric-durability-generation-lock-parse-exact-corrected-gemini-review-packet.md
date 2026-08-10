# Corrected independent veto: generation-lock parse exact digest binding

Date: 2026-08-10

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r158`
- Branch: `codex/review-context-fabric-generation-lock-parse-exact-corrected-3b35f173`
- Candidate: `3b35f173d7a09fd4a8dfb65f0716c49b4de6e7f9`
- Baseline: `9518504f66919b62a833ae6ba87c5ccbba20e65f`
- Accepted artifact source: `e115f6f4cb31df1131c5c67d24f3a475a2ca6127`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration. Return one
schema-constrained `pass` or `fail` only. Review read-only; do not edit, format,
commit, push or start Docker/PostgreSQL.

This correction supersedes the rejected r157 receipt. Do not inspect, infer,
name, hash or claim any primary-worktree-only untracked mutable evidence path.
In particular, do not substitute a tracked historical file merely because its
bytes or hash equal an absent mutable alias. Sol separately owns primary
pre/postflight checks for mutable parse and behavior evidence.

Review only tracked evidence present at exact candidate HEAD. Verify immutable
characterization
`provider-free-disposable-postgresql-evidence-generation-lock-rls-characterization.json`
has SHA-256
`78c157c72243036d395c3bcff30f778fa8b1032bb98eec9a32b37110efbcf536`,
attempt `7ab702e5fa8cd5c75a7a8e6c`, expected result
`catalogue_characterization_required`, parent artifact `aa26f926...`, parent
characterization contract `aea61c73...`, exact object populations, exact
container `aa3d7ccc...`, and verified cleanup/absence.

Reconcile it against tracked immutable immediately preceding
`provider-free-disposable-postgresql-evidence-admission-row-shape-exact-reproduction.json`.
Fourteen of fifteen acceptance-bound query digests must be identical; only
`policies` may differ. `functions` and `function_acl` must already match that
preceding generation. Reject any unexplained population or digest delta.

Verify the current contract binds exactly the fifteen characterization
digests excluding only `server` and `extensions`, uses
`exact_digest_bound`, and has canonical contract SHA-256
`dbedcaf7628a68859412d898e86292b2366209941d18f58363c45174b6fc60ba`.
The fixed harness constant must match. Historical tracked characterization and
exact-reproduction evidence must remain bound to their own immutable
expectations. Pass, characterization-required and other failures must retain
three distinct non-aliasing targets.

Reject any behavior/scenario change, new database execution, evidence alias,
provider/product data, command, deployment or protected-ref authority.

Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r158 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check 9518504f66919b62a833ae6ba87c5ccbba20e65f..3b35f173d7a09fd4a8dfb65f0716c49b4de6e7f9
git status --short --branch
git rev-parse HEAD
```

Exact count: 140 tests and three Ruff files. A pass authorizes only one later
fixed no-argument exact reproduction in one newly owned contained disposable
PostgreSQL 16 container. It does not authorize behavior, provider/product
data, commands, deployment, release, Pages or protected refs.
