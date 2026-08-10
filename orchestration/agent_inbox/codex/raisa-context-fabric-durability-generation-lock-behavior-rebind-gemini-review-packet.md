# Independent veto: generation-lock behavior parent rebind

Date: 2026-08-10

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r160`
- Branch: `codex/review-context-fabric-generation-lock-behavior-eee0e197`
- Candidate: `eee0e1976d298a054b427f32ba489de13f7c951d`
- Baseline: `2d4142ba7ff5b55ddb4e3c3c9503013bcc843aa5`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration. Return one
schema-constrained `pass` or `fail` only. Review read-only; do not edit, format,
commit, push, start Docker/PostgreSQL or write evidence.

Review only tracked files present at exact candidate HEAD. Do not inspect,
infer, name, hash or claim any primary-worktree-only untracked mutable evidence;
hash equality never permits path substitution.

Verify that the candidate changes only the behavior rehearsal's six exact
parent bindings, their deterministic assertions, the expected canonical JSON
contract digest, and the rebind/receipt ledgers. Recompute each canonical
parent hash and reconcile each non-ledger parent through `git show` at its
named source HEAD. The special accepted-runtime ledger must itself contain
exact runtime candidate `fb10f2555a246a2918d84c82e31ea5ea87f32a79`.

Verify canonical behavior contract SHA-256
`6375e756efe85caa17d99d223747b2b6e7aa59cc846f99c702a27612529f7482`.
After removing only `parent_bindings`, candidate and baseline contract objects
must be exactly equal. All twenty scenario objects and their order must remain
unchanged, with category counts `6/4/3/4/3` and canonical scenario-population
SHA-256 `7c8709c2ec1c0eb69da86fe037f551355ada6c1294e2ca4f2ce7f15ad89be5b3`.

Reject any behavior/scenario weakening, Docker/database run, evidence alias,
provider/product/patient/clinical data, runtime/API/Diary wiring, watcher/feed,
command or model-to-database write, deployment, release, Pages or protected-ref
authority.

Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r160 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
git diff --check 2d4142ba7ff5b55ddb4e3c3c9503013bcc843aa5..eee0e1976d298a054b427f32ba489de13f7c951d
git status --short --branch
git rev-parse HEAD
```

Exact count: 305 tests and three Ruff files. A pass authorizes only Sol's
separate pre-execution gate for one provider-free authored-synthetic disposable
behavior rehearsal. It does not itself start that rehearsal or open any closed
surface.
