# Independent veto packet — CF-D2 anchor-revision correction

Review id: `raisa-context-fabric-durability-restart-unknown-commit-anchor-revision-correction-gemini-36-high-veto-001`

Model: `gemini-3.6-flash-high` with high effort in one fresh Antigravity project

Exact source: `d93d55c3e6b1e28764d8b86d8ccac233d0826222`

Bound worktree: `C:\Users\sarashera\EMR4-worktrees\r188`

Bound branch: `codex/cf-d2-anchor-revision-correction-gemini-review`

## Start and authority

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a fresh read-only veto before diagnostic attempt 002. Do not edit,
create, delete, stage, commit, switch, merge, push, start or inspect Docker or
PostgreSQL, run the CF-D2 harness or diagnostic, generate evidence, contact a
provider, application route, database, credential, cloud service or network
destination, or inspect an unlisted path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-context-fabric-durability-restart-unknown-commit-recovery-descendant-plan.md`;
- `docs/raisa-context-fabric-durability-restart-unknown-commit-diagnostic-attempt-001-anchor-revision-diagnosis.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal-plan.md`;
- `docs/security/raisa-context-fabric-durability-restart-unknown-commit-recovery-descendant-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-recovery-descendant-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-recovery-descendant-contract.schema.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/restart-unknown-commit-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/provider-free-durability-restart-unknown-commit-recovery-diagnostic-evidence.schema.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-restart-unknown-commit-rehearsal/provider-free-durability-restart-unknown-commit-recovery-diagnostic-evidence-attempt-001.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert` only at the exact registration-checkpoint, first-decision revision and anchor-current-revision statements cited by the diagnosis;
- `scripts/raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py`;
- `scripts/raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py`;
- `tests/test_raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py`;
- `tests/test_raisa_context_fabric_durability_restart_unknown_commit_recovery_descendant_plan.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py`;
- `docs/ariadne-agent-error-correction-register-revision-250.md`;
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json` only at AER-0282;
- `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`;
- `tests/test_ariadne_agent_error_register.py` only at the register-wide assertions and AER-0282 test; and
- the exact diff `2d2cc5e0d0aff8166c147e1396bbea42645d7a00..d93d55c3e6b1e28764d8b86d8ccac233d0826222`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. If an unlisted direct dependency is necessary to decide,
return `revision_required` and name it without opening it.

## Required review

Decide whether exact source `d93d55c3e6b1e28764d8b86d8ccac233d0826222`
is one bounded correction that preserves CF-D2's accepted safety meaning and is
eligible for diagnostic attempt 002. Veto on any P0-P2 finding, nonzero allowed
command or material uncertainty. In particular:

1. reconcile immutable diagnostic attempt 001: all ten preconditions and the
   position-one atomic delta passed, the closed failure coordinate is exactly
   `cfd2_r01_append_anchor_2`, all external/runtime counters are zero and exact
   cleanup passed;
2. verify from the accepted inert SQL that registration creates checkpoint and
   baseline anchor lifecycle revision zero, the first applied decision advances
   the checkpoint by exactly one, and `append_recovery_anchor_v1` accepts only
   the checkpoint's current nonzero lifecycle revision;
3. decide whether passing numeric lifecycle revision one is therefore the only
   possible correction while retaining the scenario meaning that position two
   remains fenced until lifecycle authority independently anchors the complete
   position-one state;
4. verify coordinate suffix `_anchor_2` is explicitly an anchor ordinal, not
   numeric lifecycle revision, and every anchor participant passes and expects
   token `1`;
5. verify the correction changes no accepted SQL, role/RLS grant, atomic member,
   recovery classification, anchor authority, isolation, durability setting,
   scenario order, fencing meaning or claim boundary;
6. verify the schema admits exactly the immutable old failure bindings and the
   corrected future bindings, while passing evidence is semantically required
   to use only the corrected contract digests and terminal token;
7. verify attempt 001 remains immutable, only diagnostic attempt 002 and full
   attempt 003 paths are opened, and no retry or post-attempt-003 correction is
   introduced;
8. verify the new test links all five harness anchor calls to lifecycle revision
   one and the accepted SQL arithmetic/current-revision guard, and rejects
   revision two before participant rendering;
9. verify AER-0282 and revision 250 accurately report the correction without
   overstating restart or unknown-commit proof; and
10. identify any contract-digest, historical-evidence, schema,
    ordinal-versus-revision, TOCTOU, later-coordinate or claim defect that could
    make diagnostic attempt 002 unsafe or uninformative.

## Allowed commands

Run only these commands from the bound worktree, serially and without changing
environment state:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r188 tests\test_raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal_plan.py tests\test_raisa_context_fabric_durability_restart_unknown_commit_recovery_descendant_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r188-register tests\test_ariadne_agent_error_register.py::test_register_is_valid_after_durability_schema_recovery tests\test_ariadne_agent_error_register.py::test_aer_0282_corrects_the_cf_d2_anchor_revision_off_by_one tests\test_ariadne_agent_error_register.py::test_committed_pattern_report_matches_fresh_build
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py scripts\raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py tests\test_raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py scripts\raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py tests\test_raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py tests\test_raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\raisa_provider_free_disposable_postgresql_durability_restart_unknown_commit_rehearsal.py scripts\raisa_context_fabric_durability_restart_unknown_commit_recovery_diagnostic.py
git diff --check 2d2cc5e0d0aff8166c147e1396bbea42645d7a00..d93d55c3e6b1e28764d8b86d8ccac233d0826222
git status --short --branch
```

Do not run the harness, diagnostic, Docker, PostgreSQL or any other command.

Return `pass` only if every command exits zero and there are zero P0-P2
findings. In `review`, report exact HEAD, paths, command exit codes, findings
with precise file/line support, and explicit counts of Docker starts, database
operations, provider calls, product reads and external-network operations (all
must be zero). Emit exactly one schema-constrained terminal decision.
