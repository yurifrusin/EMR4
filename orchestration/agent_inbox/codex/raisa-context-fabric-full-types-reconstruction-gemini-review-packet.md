# Fresh Gemini veto: full PostgreSQL types projection reconstruction

Role: independent contract-binding and final repair veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r86`

Branch: `codex/review-context-fabric-full-types-06b8f558`

Baseline HEAD: `00d60c0f2b7f6396f5da57da887695542795f24b`

Candidate HEAD: `06b8f55837457518b39de0bdbea71b60a2c6f921`

Read-only exact-worktree review through one fresh Antigravity project. Perform
the complete five-source rehydration required by `AGENTS.md`, including the API
Steward, protected-evidence and no-runtime boundaries. Do not mutate files or
refs, start Docker, execute either PostgreSQL rehearsal, or write worktree-local
temporary state.

Treat the predecessor pass as superseded by its subsequent failed runtime.
Review the exact diff, AER-0126 and both preserved mismatch attempts. Establish
independently that:

- both attempts admitted and atomically installed the same repaired SQL and
  failed solely at `catalogue/exact_query_digest` for query id `types`;
- each exact owned container was removed and its absence verified;
- the new deterministic reconstruction includes all 32 ordered PostgreSQL type
  rows, domain definitions, enum labels and composite attributes represented by
  the `types` query;
- setting only `digest_sha256.domain_not_null=true` makes that reconstruction
  reproduce the immutable accepted characterization digest
  `sha256:099effe...` exactly;
- the complete row-level difference after setting that one flag to `false` is
  exactly one field and yields `sha256:8ec5eddf...`;
- every non-`types` query digest, artifact binding, prerequisite binding and
  containment control is unchanged; and
- AER-0126/register revision 104 truthfully records and guards against the
  incomplete-projection error.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r86 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check 00d60c0f2b7f6396f5da57da887695542795f24b..06b8f55837457518b39de0bdbea71b60a2c6f921
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only. Findings first; confirm clean unchanged
HEAD. A pass authorises exactly one fresh contained parse/catalogue rehearsal
run and nothing broader. Return exactly one schema-constrained terminal decision.
