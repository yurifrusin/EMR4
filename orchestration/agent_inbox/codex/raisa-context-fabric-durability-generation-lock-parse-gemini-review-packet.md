# Independent veto: generation-lock parse characterization rebind

Date: 2026-08-10

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r156`
- Branch: `codex/review-context-fabric-generation-lock-parse-a85224f0`
- Candidate: `a85224f095f32ab4f77cb81ae5691011eedfc1cb`
- Baseline: `661ebe93e13f35e5cdfb8cb73da1063cf8cb05c0`
- Accepted artifact source: `e115f6f4cb31df1131c5c67d24f3a475a2ca6127`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration. Return one
schema-constrained `pass` or `fail` only. Review read-only; do not edit, format,
commit, push or start Docker/PostgreSQL.

Verify the fixed parse contract binds exact source `e115f6f4...`, inert SQL
SHA-256 `aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9`,
canonical LF byte count `1435252`, statement count 421, PostgreSQL 16 and the
unchanged closed Docker profile. Its canonical contract SHA-256 must be
`aea61c7344f6b4990fed848994f63a0f42788c807477fbed1ce1d845dd579227`.

Verify current catalogue mode is exactly `characterization_only` with an empty
expected digest map. Historical admission-row-shape characterization and exact
reproduction tests must bind their own immutable expected map and historical
contract digest rather than borrow the current empty map. Confirm pass,
characterization-required and other failure results still route to three
distinct non-aliasing evidence paths.

Verify mutable accepted parse evidence remains untracked/unstaged at SHA-256
`97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec`,
protected historical exact-rerun failure remains SHA-256
`3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`,
and mutable behavior evidence remains SHA-256
`09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`.
Reject any behavior/scenario change, database execution, evidence alias,
provider/product data, command, deployment or protected-ref authority.

Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r156 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check 661ebe93e13f35e5cdfb8cb73da1063cf8cb05c0..a85224f095f32ab4f77cb81ae5691011eedfc1cb
git status --short --branch
git rev-parse HEAD
```

Exact count: 139 tests and three Ruff files. A pass authorizes only one later
fixed no-argument characterization in one newly owned contained disposable
PostgreSQL 16 container. It does not authorize exact reproduction, behavior,
provider/product data, commands, deployment, release, Pages or protected refs.
