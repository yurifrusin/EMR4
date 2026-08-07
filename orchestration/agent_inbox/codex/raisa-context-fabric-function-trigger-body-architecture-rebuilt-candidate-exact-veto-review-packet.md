# Fresh exact-HEAD veto packet: rebuilt durability function/trigger bodies

## Decision requested

Return exactly one terminal decision: `pass` only if exact candidate
`5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d` has no P0, P1 or P2 defect
within the frozen provider-free unmounted function-and-trigger-body
architecture; otherwise return `revision_required` with the smallest
reproducible findings.

This is a fresh candidate-independent veto after the rejected predecessor at
`f51f5b65dd77d9282e5325a5e4f17edd872d14df`. Do not inspect that review or
inherit its conclusions. Judge the current sources and frozen recovery
requirements independently.

## Workspace, branch and authority

- Worktree: `C:/Users/sarashera/EMR4-worktrees/r35`
- Branch: `codex/review-durability-function-trigger-body-r5`
- Exact HEAD: `5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d`
- Role: fresh read-only candidate-independent veto reviewer
- Owned files: none; this reviewer may not edit or generate repository files.
- Durable result: the exact mailbox response will be persisted by Sol at
  `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-rebuilt-candidate-exact-veto.md`.
- No edits, generation, staging, commits, pushes, branch/ref movement,
  provider/model calls, database/source/network/browser contact, SQL
  rendering/execution, app execution, runtime wiring, patient/product/clinical
  data, deployment, production, release or Pages action.
- Do not inspect prior review, rejection, AER, inbox, protected-holdout,
  branding or unrelated repository paths. Do not enumerate the repository.

## Exact readable paths

1. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-plan.md`
2. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-recovery.md`
3. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`
4. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-typed-ir-recovery.md`
5. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-exact-veto-recovery.md`
6. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-design.md`
7. `docs/security/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-threat-model-delta.md`
8. `orchestration/continuity/raisa-provider-free-unmounted-durability-migration-transaction-architecture/migration-transaction-architecture-contract.json`
9. `orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json`
10. `orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.schema.json`
11. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py`
12. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
13. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py`
14. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
15. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py`
16. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py`
17. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py`
18. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
19. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py`
20. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py`
21. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py`
22. `orchestration/api_spine_adr.md`
23. `orchestration/api_spine_programme.md`
24. `orchestration/bernie_release_gates.md`
25. `docs/api-spine/async/integration-events.yaml`
26. `docs/api-spine/openapi/diary-committed-events.yaml`
27. `docs/api-spine/graphql/practice-context-fabric-read.graphql`
28. `tests/test_api_spine_artifacts.py`

## Required independent review

1. Verify exact HEAD and a clean worktree before and after review.
2. Read the plan and all four recovery documents before judging the design.
3. Inspect the builder, all twenty-two body sources, semantic validator,
   structural schema, generated contract and tests. Passing tests and stored
   summaries are corroboration, not proof by themselves.
4. Independently challenge the exact R1 coordinator state/effect closure:
   retained receipt replay, terminal replay/integrity, every admission and
   predecessor/epoch/gap/key/anchor/dependent-state branch, and every atomic
   receipt/lifecycle/checkpoint/frame/watermark/obligation effect.
5. Independently challenge R2 retention: the complete all-except-CONSUMED
   census, exact scope and per-generation coverage, real minimum checkpoint,
   active pins, actual key overlap, source/receipt/checkpoint/audit grace,
   seconds rather than minutes, exact REC19 reasons and purge rederivation.
6. Independently challenge R3 non-temporal fencing: absence is limited to this
   exact current top-level transaction using current event, current alias,
   exact current outbox join and head movement; historical or unrelated rows
   must remain harmless, while temporal and second-update guards remain.
7. Independently challenge R4 normative closure: parent/effective-parent
   derivation, ordered recovery scalars, signatures, trigger declarations,
   roles/privileges, enums and body-derived program semantics must fail closed
   without relying on canonical byte equality or whole-body const snapshots.
8. Confirm enum NULL representation does not admit a non-null out-of-enum
   value, frozen empty arrays remain valid, and critical scalar schema closure
   cannot be bypassed by regenerating the contract/schema digests.
9. Confirm API Spine and claim ceilings remain unchanged: GraphQL read-only,
   REST commands unchanged, events observation-only, and no SQL/DDL, database,
   source, runtime, provider, product/patient data, deployment or production
   claim.

## Exact deterministic commands

Run from `C:/Users/sarashera/EMR4-worktrees/r35` with
`PYTHONDONTWRITEBYTECODE=1`:

```powershell
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests/test_api_spine_artifacts.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py
git diff --check
git status --short
git rev-parse HEAD
```

You may run additional in-memory read-only challenges over the exact readable
paths, but may not create, modify or regenerate files.

## Response shape

Report exact HEAD, exact files inspected, commands and outcomes, independent
R1-R4 challenges, findings by severity, claim-boundary assessment and unchanged
worktree postcondition. Wait for every command to finish, then end once with
exactly one final line:

`DECISION: pass`

or

`DECISION: revision_required`
