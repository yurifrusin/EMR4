# Independent veto: admission replay winner recovery

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

Review clean worktree
`C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-behavior-r176`
on branch `codex/review-context-fabric-admission-replay-5a9a7ae9` at exact
candidate `5a9a7ae907308aa0a8a4256e9043b833f8c416ae`, predecessor
`5237a083`. Protected local/origin `master` and `handoff/current` must remain
exactly `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration naming
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md; exact diff `5237a083..5a9a7ae9`; immutable attempt-046
failure/diagnosis and their bounded script/test/doc; renderer, generated inert
artifacts, renderer tests, AER 0234/0235 and the candidate precommit receipt.
Do not inspect the mutable behavior evidence alias, holdouts, historical Diary
data, `docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before/after, exact branch/diff and protected refs;
2. attempt 046 SHA-256
   `ea2fc7f55121604b8f68b5bbacc55b97c98ead76a5793b6d7c766f2269b311c0`
   is one bounded BTR-I02 CF004 failure with complete cleanup and no rerun;
3. repository diagnosis proves all three admission INSERT_OR_RELOAD_COMPARE
   nodes inserted `admitted_at` from transaction timestamp and incorrectly
   compared the stored winner to the later transaction timestamp;
4. renderer 2.0.20 adds exactly one sealed
   `NORMALIZE_ADMISSION_RELOAD_WINNER_PREDICATES` effective operation;
5. only the admitted-at timestamp equality is removed from those three winner
   predicates; admitted-at insertion, storage, return, winner columns, exact
   conflict keys and every stable comparison remain unchanged;
6. immutable structural/body parents, roles, capabilities, RLS, SQLSTATE,
   transaction and command boundaries remain unchanged;
7. regenerated inert SQL is exactly 424 statements, 1,436,664 LF bytes and
   SHA-256 `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`;
8. render manifest SHA-256 is
   `2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271`;
9. AER revision 201 contains 235 closed incidents through AER-0235;
10. all checks below pass with a clean postcondition; and
11. no Docker/PostgreSQL run, operational database, watcher/feed,
    application/API/Diary wiring, provider/product data, deployment, Pages or
    protected-ref boundary opens.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r176 tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis.py tests\test_ariadne_agent_error_register.py tests\test_ariadne_orchestrator_preflight.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py scripts\raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py tests\test_raisa_context_fabric_durability_behavior_failure_046_admission_replay_diagnosis.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_unmounted_durability_inert_ddl_rehearsal check
git diff --check 5237a083..5a9a7ae9
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run either disposable
database harness, contact another provider/product, inspect forbidden data,
move refs or self-accept. Return `revision_required` for any P0-P2 finding,
drift, failed check or dirty postcondition; otherwise return exact `pass`.
