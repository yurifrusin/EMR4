# Fresh Gemini veto: Context Fabric behavior-transaction rehearsal

Role: independent deterministic-proofreader, database-boundary and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r75`

Branch: `codex/review-context-fabric-behavior-efeb5c68`

Baseline HEAD: `324d37f086a51a60b260d02b38772594b6c205df`

Candidate HEAD: `efeb5c686977fb8a2d2c34ec2c65b5ed2cd0637c`

Review only in this exact clean worktree through one genuinely fresh
Antigravity project. Do not edit, create, delete, stage, commit, push, deploy,
open Docker/PostgreSQL, inspect another worktree, or inspect historical provider
material. Do not write temporary artifacts inside the worktree. Protected
evidence, credentials, patient/clinical/document/product-derived/real-identity
data, provider calls, runtime gates and `docs/branding/` are forbidden.

Before review, read `AGENTS.md` completely. Perform its full five-source
rehydration from `live_handover_current_baton`,
`current_authority_allocation`, `active_plan_and_acceptance`,
`protected_evidence_boundaries`, and `git_refs_and_worktree`; state those five
sources in your report. Read the EMR4 API Steward skill/checklist completely.
Inspect only the baseline-to-candidate diff and the named parent/candidate
artifacts. Do not perform broad discovery.

Adversarially determine whether the candidate is safe to admit for exactly one
provider-free disposable PostgreSQL 16 behavior run. In particular verify:

- the Agent Execution Surface and Containment Gate is placed after the current
  provider-free Context Fabric durability sequence and before any real
  product-derived context or executable occupied Bureau/tool/runtime, without
  granting present execution authority;
- the broker, manifest, identity, egress, cumulative-budget, generation,
  revocation, context-inertness, supply-chain and kill-switch requirements are
  deterministically external to any model, and GraphQL remains non-mutating;
- the harness accepts no caller arguments or data, verifies the canonical
  contract and six parent bindings before Docker, and is fixed to one
  networkless, mountless, portless, socket-only, passwordless, non-listening,
  resource-bounded, PostgreSQL 16 container with exact owned cleanup;
- all 20 scenario IDs are closed and executed in contract order with one fresh
  scenario process/connection, exact role, isolation, read-only, SQLSTATE,
  failure-id/reason, before/after/readback and forbidden-effect assertions;
- `BTR-T01` alone proves the deferred `CF603` commit-time obligation guard;
  `BTR-T02` proves the immediate `CF601` reschedule-event DELETE guard; and
  `BTR-T03` reaches the authorised application-event UPDATE path and proves its
  immediate `CF601` immutability guard without an impossible Fabric grant;
- `BTR-R03` uses five fresh denied connections, `BTR-R01` proves beta-practice
  invisibility over all three application projections, and `BTR-B01` expects
  the pre-existing position-one audit plus the new position-two audit;
- the evidence schema position-closes all 20 records and cannot carry SQL,
  credentials, raw rows, patient/product material or an unenumerated outcome;
- pre-runtime validation cannot start Docker after any binding, schema,
  catalogue, fixture or invariant failure; cleanup retains a separate bounded
  reserve; and no provider, network, deployment, Pages, protected-ref,
  production or product-data authority has leaked in;
- AER-0113 and AER-0114 accurately preserve the rehydration and scenario-design
  failures and the corrected contract is the one bound by the implementation.

Run only these commands; pytest cache is disabled and base temp is outside the
repository:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r75 tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_ariadne_agent_error_register.py
git diff --check 324d37f086a51a60b260d02b38772594b6c205df..efeb5c686977fb8a2d2c34ec2c65b5ed2cd0637c
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only and require no worktree-local temporary
files. List findings first by severity, name each check run, confirm unchanged
exact HEAD and clean worktree, distinguish observation from inference, and name
claims not established. A pass authorises only the single already-planned
provider-free disposable database rehearsal; it does not establish its runtime
result. End with exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
