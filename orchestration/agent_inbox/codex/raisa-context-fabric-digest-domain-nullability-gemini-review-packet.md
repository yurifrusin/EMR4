# Fresh Gemini veto: digest-domain nullability recovery

Role: independent PostgreSQL architecture and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r82`

Branch: `codex/review-context-fabric-digest-nullability-580c1d05`

Baseline HEAD: `243c70b9a7debc530b6352c82a3bbb84981f6f5a`

Candidate HEAD: `580c1d05ed150cdfd63549f1a35e61c72a41cb20`

Read-only exact-worktree review through one fresh Antigravity project. Do not
mutate files/refs, start Docker/PostgreSQL, inspect another worktree or write
worktree-local temporary state. Providers, credentials, protected evidence,
patient/clinical/document/product-derived/real-identity data and
`docs/branding/` are forbidden.

Read `AGENTS.md` completely and name all five rehydration sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Read the EMR4 API Steward skill/checklist, the new
digest-domain recovery and its threat-model delta, the behavior implementation
recovery, failure evidence 007 and AER-0123.

Review the exact baseline-to-candidate diff. Verify empirically that:

- the old domain-level `NOT NULL`, nullable
  `context_durability_checkpoint.last_observation_digest`, `ck_cf_07_03`, and
  registration function's typed position-zero null were mutually
  unrepresentable in PostgreSQL;
- `RELAX_DIGEST_DOMAIN_NULLABILITY` changes only the effective
  `digest_sha256.not_null_values` flag and is old/new fragment-sealed;
- the digest format check remains exact and every mandatory digest column
  retains column-level `NOT NULL`;
- `ck_cf_07_03` still requires null at zero and non-null above zero;
- immutable parent hashes, 412-statement population, functions, triggers,
  roles, grants, RLS, transaction and containment boundaries remain unchanged;
- canonical SQL, manifest and lowering files exactly equal a fresh renderer
  result;
- old PostgreSQL evidence is not treated as evidence for this candidate; and
- the candidate grants no migration, runtime, provider, product-data,
  deployment or protected-ref authority.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r82 tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_postgresql_representability_recovery.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 243c70b9a7debc530b6352c82a3bbb84981f6f5a..580c1d05ed150cdfd63549f1a35e61c72a41cb20
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only. Findings first; confirm clean unchanged
HEAD and separate observation from inference. A pass authorises only contract
rebinding and a fresh parse/catalogue review cycle, not Docker execution by the
reviewer. End exactly `DECISION: pass` or `DECISION: revision_required`.
