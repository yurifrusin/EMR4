# Independent evidence veto: generation-lock parse exact reproduction

Date: 2026-08-10

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r159`
- Branch: `codex/review-context-fabric-generation-lock-parse-reproduction-fb10f255`
- Candidate: `fb10f2555a246a2918d84c82e31ea5ea87f32a79`
- Baseline: `97d71063c9f9f8629c70581a1b38d76cdd353ed1`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration. Return one
schema-constrained `pass` or `fail` only. Review read-only; do not edit, format,
commit, push or start Docker/PostgreSQL.

Review only tracked evidence present at exact candidate HEAD. Do not inspect,
infer, name, hash or claim primary-worktree-only untracked mutable evidence;
hash equality never permits path substitution.

Verify immutable exact reproduction
`provider-free-disposable-postgresql-evidence-generation-lock-rls-exact-reproduction.json`
has SHA-256
`c82ebc7a0ec45ab2d01b55e33f14adaf120a2f65d9e7f151757a65e4d482e68b`,
attempt `9f71b0e4f0c8f99ab8a6f2d1`, terminal result
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`,
catalogue `matched`, expectation mode `exact_digest_bound`, artifact
`aa26f926...`, exact contract `dbedcaf7...`, exact container `fdd29923...`,
and cleanup/absence true.

Recompute that every complete query digest and object population equals the
tracked immutable generation-lock characterization. Verify the focused test
binds exact evidence file hash, attempt, parent, digest map, populations and
cleanup. Historical evidence must remain bound to its own immutable
expectations. The prior r157 path-misreport receipt remains rejected; the
corrected r158 veto remains the only admitted pre-execution review.

Reject any behavior/scenario change, database rerun, evidence alias,
provider/product data, command, deployment or protected-ref authority.

Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r159 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check 97d71063c9f9f8629c70581a1b38d76cdd353ed1..fb10f2555a246a2918d84c82e31ea5ea87f32a79
git status --short --branch
git rev-parse HEAD
```

Exact count: 141 tests and three Ruff files. A pass admits this parse evidence
only for a separately committed behavior-parent rebind. It does not authorize
a behavior run, provider/product data, commands, deployment, release, Pages or
protected refs.
