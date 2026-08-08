# Fresh Gemini veto: behavior fixture dependency-chain repair

Role: independent PostgreSQL foreign-key, deterministic-proofreader and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r77`

Branch: `codex/review-context-fabric-behavior-fixture-7ac63adf`

Repair baseline HEAD: `db0f7c5e1281a220d6eaf1d0c94116597af169d8`

Candidate HEAD: `7ac63adfe9ccd3d72437235a14730ce06fe6b7a4`

Review only in this exact clean worktree through one fresh Antigravity project.
Do not edit/create/delete/stage/commit/push/deploy, open Docker/PostgreSQL,
inspect another worktree or write worktree-local temporary artifacts. Protected
evidence, credentials, patient/clinical/document/product-derived/real-identity
data, provider calls, runtime gates and `docs/branding/` are forbidden.

Read `AGENTS.md` completely, perform and report its five-source rehydration from
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`, then read the EMR4 API Steward skill/checklist. Inspect
only this exact repair diff, failure evidence 002, the accepted inert DDL's
named foreign keys, AER-0116, recovery note, harness and tests.

Adversarially verify:

- failure 002 is schema-valid and proves catalogue reconciliation followed by
  `fixture/bootstrap_failed`, zero scenarios and exact verified cleanup;
- the prior beta fixture violated `fk_cf_06_01` (generation needs barrier) and
  `fk_cf_11_01` (watermark needs checkpoint), and no earlier accepted boundary
  better explains this first-effective failure;
- the new data-modifying CTE chain makes each child read its required parent in
  exact order: barrier → observer generation → durability checkpoint → frame,
  then watermark from checkpoint and obligation from frame;
- all required columns, enum values, domains, checks and foreign keys for those
  six relations are satisfied, and the original application-read proof still
  sees exactly the intended beta frame, watermark and obligation rows;
- the fixture remains authored-synthetic, private to the disposable database,
  and changes no application/Fabric DDL, accepted contract, scenario, grant,
  role, RLS, trigger, containment or claim;
- AER-0116 and revision 96 accurately preserve the failure and the topology-DAG
  prevention control.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r77 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check db0f7c5e1281a220d6eaf1d0c94116597af169d8..7ac63adfe9ccd3d72437235a14730ce06fe6b7a4
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only and need no worktree-local temp. Findings
come first; confirm unchanged exact HEAD and clean worktree, distinguish
observation from inference and name claims not established. A pass authorises
only one corrected provider-free disposable PostgreSQL 16 rerun and does not
establish its result. End with exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
