# Exact-head independent veto packet: durability function/trigger bodies

## Decision requested

Return exactly one terminal decision: `pass` only if exact candidate
`f51f5b65dd77d9282e5325a5e4f17edd872d14df` has no P0, P1 or P2 defect within
the frozen function-and-trigger-body architecture; otherwise return
`revision_required` with the smallest reproducible findings.

## Workspace and authority

- Worktree: `C:/Users/sarashera/EMR4-worktrees/r33`
- Branch: `codex/review-durability-function-trigger-body-f51f5b65`
- Exact HEAD: `f51f5b65dd77d9282e5325a5e4f17edd872d14df`
- Role: fresh read-only candidate-independent veto reviewer
- No edits, staging, commits, pushes, branch/ref movement, provider/model calls,
  database/source/network/browser contact, SQL rendering/execution, app
  execution, runtime wiring, patient/product/clinical data, deployment,
  production, release or Pages action.
- Do not inspect prior review, rejection, AER, inbox, protected-holdout,
  branding or unrelated repository paths. Do not enumerate the repository.

## Exact readable paths

1. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-plan.md`
2. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-recovery.md`
3. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`
4. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-typed-ir-recovery.md`
5. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-design.md`
6. `docs/security/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-threat-model-delta.md`
7. `orchestration/continuity/raisa-provider-free-unmounted-durability-migration-transaction-architecture/migration-transaction-architecture-contract.json`
8. `orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json`
9. `orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.schema.json`
10. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py`
11. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
12. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py`
13. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
14. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py`
15. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py`
16. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
17. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py`
18. `orchestration/api_spine_adr.md`
19. `orchestration/api_spine_programme.md`
20. `orchestration/bernie_release_gates.md`
21. `docs/api-spine/async/integration-events.yaml`
22. `docs/api-spine/openapi/diary-committed-events.yaml`
23. `docs/api-spine/graphql/practice-context-fabric-read.graphql`
24. `tests/test_api_spine_artifacts.py`

## Required independent review

1. Verify exact HEAD and clean worktree before and after review.
2. Read the plan and all three recovery documents before judging the design.
3. Inspect the builder, all twenty-two body sources, semantic validator,
   structural schema, generated contract and tests. Do not treat passing tests
   or stored summaries as proof by themselves.
4. Independently challenge whether operands truly determine reads, writes,
   locks, calls, failures, trigger images, terminals and outputs; whether the
   validator is path-sensitive where needed; and whether the schema blocks
   otherwise valid elements transplanted to a wrong body or position.
5. Reproduce the focused 126-test packet and API Spine checks with the exact
   repository interpreter. You may add read-only in-memory challenge commands,
   but may not create or modify files.
6. Check the nineteen required hostile classes, especially wrong-relation DML,
   missing head update, illegal cross-relation trigger image, source-before-
   authentication admission, terminal replay from unassigned/input values,
   lock reorder, widened product read, call cycle, swapped signatures or
   declarations, raw SQL, transaction control and authority widening.
7. Confirm the claim ceiling: this is machine-readable unmounted architecture
   only, not SQL/DDL, PostgreSQL execution, database/runtime/source/provider,
   product/patient data, command, deployment or production evidence.

## Exact deterministic commands

Run from `C:/Users/sarashera/EMR4-worktrees/r33` with
`PYTHONDONTWRITEBYTECODE=1`:

```powershell
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_api_spine_artifacts.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py
git diff --check
git status --short
git rev-parse HEAD
```

## Response shape

Report exact HEAD, files inspected, commands and outcomes, independent
challenges, findings by severity, boundary assessment and unchanged-worktree
postcondition. End with exactly one final line:

`DECISION: pass`

or

`DECISION: revision_required`
