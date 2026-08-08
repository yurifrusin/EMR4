# Fresh Gemini veto: behavior catalogue database-binding repair

Role: independent deterministic-proofreader, PostgreSQL-boundary and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r76`

Branch: `codex/review-context-fabric-behavior-repair-db0f7c5e`

Repair baseline HEAD: `efeb5c686977fb8a2d2c34ec2c65b5ed2cd0637c`

Candidate HEAD: `db0f7c5e1281a220d6eaf1d0c94116597af169d8`

Review only in this exact clean worktree through one genuinely fresh
Antigravity project. Do not edit/create/delete/stage/commit/push/deploy, open
Docker/PostgreSQL, inspect another worktree, or inspect historical provider
material. Do not write temporary artifacts inside the worktree. Protected
evidence, credentials, patient/clinical/document/product-derived/real-identity
data, provider calls, runtime gates and `docs/branding/` are forbidden.

Read `AGENTS.md` completely and perform its five-source rehydration from
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`; name all five in the report. Read the EMR4 API Steward
skill/checklist completely. Inspect only the exact repair diff and the named
failure evidence, recovery note, AER-0115, harness and tests.

Adversarially verify:

- failure attempt 001 is schema-valid, immutable, has the exact
  `catalogue/server_or_database` boundary, zero scenarios and verified exact
  container cleanup;
- the failure is correctly explained by direct reuse of the accepted parent's
  fixed `emr4_synthetic_success` sentinel for the descendant's independently
  fixed `emr4_synthetic_behavior` database;
- `_assert_bound_parent_catalogue` fails closed unless the original observed
  facts prove exactly the descendant database and PostgreSQL major 16;
- it deep-copies those facts, changes only the copy's database name to the
  parent's private sentinel, leaves the original evidence unchanged, and calls
  the unchanged parent assertion for all other catalogue checks;
- the adapter cannot mask a wrong database, missing/malformed server object,
  non-16 major version or any downstream parent structural failure;
- no contract, scenario, role, grant, RLS, trigger, SQL, runtime containment,
  provider/data/deployment/Pages/protected-ref boundary or claim was broadened;
- AER-0115 and revision 95 accurately preserve the failed attempt and require
  this exact fresh veto before any second run.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r76 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check efeb5c686977fb8a2d2c34ec2c65b5ed2cd0637c..db0f7c5e1281a220d6eaf1d0c94116597af169d8
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only and require no worktree-local temporary
files. Findings come first. Confirm unchanged exact HEAD and clean worktree,
distinguish observation from inference and name claims not established. A pass
authorises only one corrected provider-free disposable PostgreSQL 16 rerun; it
does not establish that runtime result. End with exactly one terminal line:
`DECISION: pass` or `DECISION: revision_required`.
