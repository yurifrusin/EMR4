# Independent veto: receipt-lock behavior-parent rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r170`
- Branch: `codex/review-context-fabric-receipt-lock-behavior-ba25816d`
- Accepted parse baseline: `662fcae68308061faf09f4b3a8820baeaa417d88`
- Candidate: `ba25816d65b4f50dfc2d71bb0ed1ead44166c5cd`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration and name
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md, diff `662fcae6..ba25816d`, the exact six parent
artifacts named by the behavior contract, the receipt-lock recovery/rebind
documents, immutable attempt/diagnosis 042, the behavior script/tests, the
register/pattern report/revisions 189-191, and this packet/receipt/preflight.
Do not inspect mutable evidence, protected holdouts, historical Diary data,
`docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before and after review, exact branch and exact diff;
2. immutable attempt 042 and diagnosis still bind BTR-I03, SQLSTATE `CF004`,
   `apply_durability_transition_v1` line 210, exact cleanup absence, and zero
   diagnosis reruns;
3. line 210 is the missing-row exception after the classified-observation
   receipt `FOR UPDATE` lock, while the preceding ordinary receipt-set read
   observed exactly one row;
4. structural source `a1af31e89c13a0eea72fd90a2934a0c8e0154175`
   adds only `pol_cf_09_update_lock`, whose `USING` is exact coordinator
   session binding and whose identical `WITH CHECK` ends `AND FALSE`;
5. coordinator direct-table DML remains empty, the receipt remains immutable,
   and no role, grant, security-definer owner or authority ceiling widens;
6. body source `206803a26767d7be02b45514dd02c56cce773a46`
   changes no typed function/trigger program meaning and binds the repaired
   structural parent;
7. inert source `1b37d217779a5d7c3a9876a50db8f2f7099dfb23`
   has exactly 1,437,022 LF bytes, 424 statements, SQL SHA-256
   `bfd8fd924a1771ea03a2395fbd1f154253f098a3e488188a2f77778c197d7f38`
   and manifest-file SHA-256
   `dd4d98a8760487b17c0a70b08ef290c45607c71284a7cef804db126faac17cc6`;
8. exact parse evidence source
   `662fcae68308061faf09f4b3a8820baeaa417d88` has SHA-256
   `67a490639840e217b740474afc331ab8aced5fb84871329099df6f504739288b`,
   result pass, all 17 exact catalogue digests, 48 policies and exact owned
   container cleanup;
9. all six behavior parents resolve byte-exactly from their source commits;
10. rebound behavior contract canonical SHA-256 is
    `ee44dbf39c2458fdabc94768e3c3e8cdcc0372c10ae7f0a35709b55301c5d596`;
11. the exact twenty scenarios, order, principals, SQLSTATEs, effects,
    rollback rules, relation allowlists, category counts `6/4/3/4/3` and
    canonical scenario-set digest
    `d83130af81fffe6d4fd2c404cd6a9376fc7d77332095399b023998c8c2bf92b9`
    are unchanged;
12. attempts 001-042 and protected mutable evidence remain excluded, and no
    database or Docker action has followed attempt 042;
13. AER revision 191 contains exactly 220 closed incidents through AER-0220;
    the two failed parent-rebind receipts are preserved and the distinct v2
    receipt reproduces as passed;
14. no applied migration, operational database, watcher/feed, application,
    API/Diary wiring, provider, patient/clinical/product data, command/write,
    deployment, Pages or protected-ref boundary opens; and
15. the checks below pass and the checkout remains clean.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r170 tests\test_ariadne_agent_error_register.py tests\test_raisa_context_fabric_durability_behavior_failure_040_obligation_scope_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_041_rejection_precedence_diagnosis.py tests\test_raisa_context_fabric_durability_behavior_failure_042_receipt_lock_rls_diagnosis.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests\test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests\test_raisa_provider_free_unmounted_durability_migration_transaction_architecture_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
git diff --check 662fcae68308061faf09f4b3a8820baeaa417d88..ba25816d65b4f50dfc2d71bb0ed1ead44166c5cd
git status --short --branch
git rev-parse HEAD
```

Do not edit, commit, push, start Docker/PostgreSQL, run either runtime harness,
contact any other provider/product, inspect forbidden data, move refs or
self-accept. Return `revision_required` for any P0-P2 finding, drift, failed
check or dirty postcondition; otherwise return exact `pass`.
