# Fresh Gemini veto: allowlisted fixed not-null header

Role: independent evidence-egress and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r81`

Branch: `codex/review-context-fabric-not-null-header-243c70b9`

Baseline HEAD: `6c52d760a80c86703a245febe07505266a44cb27`

Candidate HEAD: `243c70b9a7debc530b6352c82a3bbb84981f6f5a`

Read-only exact-worktree review through one fresh Antigravity project. Do not
mutate files or refs, start Docker/PostgreSQL, inspect another worktree, or write
worktree-local temporary state. Providers, credentials, protected evidence,
patient/clinical/document/product-derived/real-identity data and
`docs/branding/` are forbidden.

Read `AGENTS.md` completely and name all five rehydration sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Then read the EMR4 API Steward skill/checklist and the
active behavior-rehearsal plan, design, threat-model delta and implementation
recovery record.

Inspect only the baseline-to-candidate diff, failure evidence 006, AER-0122,
the harness parser and its tests. Verify that:

- the fallback is attempted only for SQLSTATE `23502` when the separately
  labelled diagnostic coordinates are unavailable;
- the regex accepts only the exact PostgreSQL English not-null header shape and
  lowercase identifier grammar, with no generic free-text parsing;
- a header-derived identifier pair is released only after mapping to exactly
  one relation in `SAFE_BOOTSTRAP_COLUMNS` and an allowlisted column;
- unlisted, missing or ambiguous coordinates release no identifiers or raw
  output;
- failure evidence 006 remains zero-scenario, fail-closed and cleanup-complete;
- no SQL, fixture, scenario, DDL, role, grant, RLS, containment, claim,
  provider, product-data or protected-ref boundary changed.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r81 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 6c52d760a80c86703a245febe07505266a44cb27..243c70b9a7debc530b6352c82a3bbb84981f6f5a
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only. Findings first; confirm clean unchanged
HEAD and separate observation from inference. A pass authorises one diagnostic
rerun only. End exactly `DECISION: pass` or `DECISION: revision_required`.
