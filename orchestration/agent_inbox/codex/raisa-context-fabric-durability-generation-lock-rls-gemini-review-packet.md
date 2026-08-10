# Independent veto: durability generation-lock RLS recovery

Date: 2026-08-10

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r155`
- Branch: `codex/review-context-fabric-generation-lock-rls-e115f6f4`
- Candidate: `e115f6f4cb31df1131c5c67d24f3a475a2ca6127`
- Baseline: `4385dfcb926109b6e8c310e075a2e1c5e5c543cc`
- Protected refs: exact `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the complete five-source `AGENTS.md` rehydration. Return one
schema-constrained `pass` or `fail` only. Review read-only; do not edit, format,
commit, push or start Docker/PostgreSQL.

Verify immutable behavior failure 035 is exact SHA-256
`9ee9265487f0c14ea7987f979166e6b900241cbb820a9faa522eab14aea0d7d5`,
stopped before any scenario committed at `BTR-E04`, SQLSTATE `CF004`, function
line 143, and records verified exact-ID cleanup. Verify deterministic diagnosis
SHA-256 `b761987f82d71ad4194b5f60c5e5224a00c4942fa5a92119918a604b8af374ad`
maps that line to the `context_observer_generation` `FOR UPDATE` typed node,
shows ten bounded coordinator-owned generation updates, and opened zero further
containers.

Verify the repair changes only the existing `pol_cf_06_update` capability
predicate from `LIFECYCLE` to exact ordered `COORDINATOR, LIFECYCLE` in both
USING and WITH CHECK. `context_coordinator` must retain empty direct table
SELECT and DML lists and only the pre-existing
`apply_durability_transition_v1` execute grant. Reject any new role, bypass-RLS,
direct relation privilege, entry point, typed-body node, scenario, product or
external authority.

Verify canonical structural contract digest
`3ce317803da9cbd1a38a1f922627784467b3e8cc7e34dac924c09c4be6bf6a16`,
unchanged-body rebind digest
`32edb340c490d509015bcafe9fecddb1057400a14c537f5d3fdb4bbfee6d3e9c`,
and regenerated 421-statement inert SQL SHA-256
`aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9`.
Confirm the parse and behavior contracts remain deliberately bound to their
last accepted parents and are therefore ineligible until a later committed
rebind, fresh parse proof and fresh veto. Mutable behavior evidence must remain
untracked/unstaged at protected SHA-256
`09907bf6569944f51fe0c13ba2b07f118e9f151173a19c188837e4e2a0deb12b`.

Run exactly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r155 tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts\raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_035_generation_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
git diff --check 4385dfcb926109b6e8c310e075a2e1c5e5c543cc..e115f6f4cb31df1131c5c67d24f3a475a2ca6127
git status --short --branch
git rev-parse HEAD
```

Exact count: 201 tests and ten Ruff files. A pass authorizes only the later
repository rebind/characterization sequence; it does not authorize a database
run, provider/product data, commands, deployment, release, Pages or protected
ref movement.
