# Corrected independent veto: admission-lock behavior rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r165`
- Branch: `codex/review-context-fabric-admission-lock-corrected-8ae67f6b`
- Diagnosed-failure baseline: `444f57b9a343bf3b542bc222b4c11bde49b6ce1a`
- Behavior-rebind source: `3cbaa4cb68acb78370183947a315f946f8d0ddaa`
- Corrected candidate: `8ae67f6b0150ce7621f49c92c2f83bde1d46418e`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and explicitly name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## First-review disposition

The committed first-review packet and r164 receipt are authoritative failure
provenance. Fresh Gemini 3.6 Flash/high review at exact `3cbaa4cb...` passed all
seventeen substantive admission-lock, parent, parse, behavior and authority
challenges, but correctly returned `revision_required` because
`test_seed_separates_agent_behavior_from_transport` expected 131
agent-behavior incidents while the register contained 133 after AER-0209 and
AER-0210. The r164 worktree remained exact and clean; no runtime opened.

Independently verify the complete baseline-to-corrected-candidate recovery and
decide whether `8ae67f6b...` fixes only that repository bookkeeping defect,
preserves the database semantics accepted by the first review, and leaves a
complete clean exact-head packet. Prior prose is context, not acceptance;
rerun every command and challenge.

## Allowed surface

Use the exact allowlist and forbidden-path boundaries from the committed first
packet
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-admission-lock-behavior-rebind-gemini-review-packet.md`.
Additionally inspect only:

- the committed first r164 review receipt and preflight/dispatch evidence;
- `docs/ariadne-agent-error-correction-register-revision-183.md`;
- AER-0211 in the register;
- regenerated `pattern-report.json`; and
- the complete `tests/test_ariadne_agent_error_register.py`.

Do not inspect protected holdouts, historical Diary material, `docs/branding/`,
patient/clinical/product-derived data or unrelated paths. Do not use
repository-wide content search outside the exact allowlist.

## Required challenges

1. Re-run and report all seventeen challenges in the committed first packet
   against exact corrected candidate `8ae67f6b...`.
2. Verify `3cbaa4cb..8ae67f6b` changes no structural, body, inert SQL, parse,
   behavior-contract or runtime semantics; it contains only first-review
   provenance, revision 183, register/pattern reconciliation and focused test
   correction.
3. Verify AER-0211 accurately preserves the r164 `revision_required` result as
   recurring signature
   `repository.agent_error_register_exact_count_update_incomplete`, without
   attributing the repository defect to Gemini reasoning.
4. Verify revision 183 has exactly 211 sequential closed incidents: origin
   counts `agent_behavior=133`, `harness=22`, `repository=47`, `transport=9`;
   category `repository_defect=47`; candidate state
   `accepted_candidate_changed=68`; and recurring pattern IDs exactly
   `AER-0175`, `AER-0179`, `AER-0211`.
5. Verify `test_seed_separates_agent_behavior_from_transport` now expects 133,
   every revision/ID/aggregate expectation is exact, the whole register file
   passes, and no stale 131 seed remains.
6. Reconfirm the admission-lock policy remains lock-only, the coordinator has
   zero direct admission DML, BTR-R03 has eight fresh denial connections, the
   twenty scenarios and `6/4/3/4/3` counts are unchanged, and all exact parent
   hashes/evidence from the first packet still match.
7. Run the complete command packet below with no test omission, plus Ruff and
   exact diff hygiene.
8. Verify exact corrected HEAD and a clean unchanged checkout before and after.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r165 tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_037_admission_lock_rls_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 444f57b9a343bf3b542bc222b4c11bde49b6ce1a..8ae67f6b0150ce7621f49c92c2f83bde1d46418e
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions and decision rule

Do not edit, format, commit, push, start Docker/PostgreSQL, run a runtime
harness, contact a product/provider surface, access patient/clinical/product
or protected data, inspect `docs/branding/`, move refs or accept your own
output.

Return `fail` for any P0-P2 finding, authority widening, parent/scenario drift,
test failure, dirty postcondition or incomplete packet. Otherwise return exact
`pass` with findings, commands/counts, exact HEAD and cleanliness.
