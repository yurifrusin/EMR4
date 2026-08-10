# Replacement independent veto: receipt-lock behavior rebind clean checkout

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r171`
- Branch: `codex/review-context-fabric-receipt-lock-behavior-repair-38c8b1cf`
- Rejected predecessor: `ba25816d65b4f50dfc2d71bb0ed1ead44166c5cd`
- Replacement candidate: `38c8b1cf3635e0f96d7200bda8c7d8b23e2b9b30`
- Accepted parse baseline: `662fcae68308061faf09f4b3a8820baeaa417d88`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md, diffs `662fcae6..38c8b1cf` and
`ba25816d..38c8b1cf`, the predecessor packet/receipt, replacement recovery,
the failure-042 diagnosis script/test and immutable evidence, the six behavior
parents, behavior contract/script/tests, AER revisions 189-192 plus
register/pattern report, and this packet/receipt/preflight. Do not inspect
mutable evidence, protected holdouts, historical Diary data, `docs/branding/`,
patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before/after, exact branch and both exact diffs;
2. predecessor Gemini receipt is structured `revision_required`, unchanged at
   exact `ba25816d`, and accepted all substantive receipt-lock, parent,
   behavior, scenario and boundary challenges;
3. the predecessor's only findings were two failure-042 tests depending on the
   absent untracked mutable alias and Ruff format drift in the register test;
4. replacement diff makes no structural, body, DDL, manifest, parse, behavior
   contract, scenario, principal, SQLSTATE, effect, role, grant or authority
   change;
5. `build_evidence` still always verifies immutable failure-042 SHA-256
   `88cd6fb34ffb07895dc9bc11c4712f64dedc24394e6befa04b70b09a7d3184d7`
   and only reads the protected mutable alias behind an existence guard;
6. clean-checkout absence is explicitly tested and a present wrong alias still
   fails with `protected_mutable_evidence_not_restored`;
7. the clean r171 checkout actually lacks the untracked mutable alias while
   the exact failure-042 diagnosis tests pass;
8. every changed Python file passes Ruff lint and Ruff format;
9. AER revision 192 contains exactly 223 closed incidents through AER-0223;
   AER-0221 accurately records the pre-Git PowerShell parse error, AER-0222
   records the recurrent clean-checkout dependency and AER-0223 records the
   recurrent touched-Python format omission;
10. the rejected review and every passed/rejected orchestrator receipt remain
    immutable, five-source complete and status-consistent;
11. the six behavior parents remain byte-exact, behavior contract canonical
    SHA-256 remains
    `ee44dbf39c2458fdabc94768e3c3e8cdcc0372c10ae7f0a35709b55301c5d596`,
    and the unchanged twenty-scenario digest remains
    `d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`;
12. no attempt 043, Docker/PostgreSQL, applied migration, operational database,
    watcher/feed, application/API/Diary wiring, patient/clinical/product data,
    command/write, deployment, Pages or protected-ref boundary opens; and
13. all exact checks below pass with clean postcondition.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r171 tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_041_rejection_precedence_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_ariadne_agent_error_register.py
git diff --check 662fcae68308061faf09f4b3a8820baeaa417d88..38c8b1cf3635e0f96d7200bda8c7d8b23e2b9b30
git diff --check ba25816d65b4f50dfc2d71bb0ed1ead44166c5cd..38c8b1cf3635e0f96d7200bda8c7d8b23e2b9b30
git status --short --branch
git rev-parse HEAD
```

Do not edit, commit, push, start Docker/PostgreSQL, run either runtime harness,
contact any other provider/product, inspect forbidden data, move refs or
self-accept. Return `revision_required` for any P0-P2 finding, drift, failed
check or dirty postcondition; otherwise return exact `pass`.
