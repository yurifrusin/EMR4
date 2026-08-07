# R6 parent-constraint and audit-chain correction worker result

- Role: bounded correction worker; no acceptance or integration authority
- Recovery-control source HEAD: `2b3798f8`
- Rejected uncommitted contract: `sha256:49db11e74a46d1056e694614a970037cf021e174d71114f5262e950b9075b01f`

## Changed paths

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
2. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-parent-correction-worker.md`

## Parent and audit corrections

- `rotate_observation_key_v1` now emits typed `pg_catalog.bigint` NULL for lifecycle `source_position`; its checkpoint update continues to omit both position and observation fields.
- KEY_ROTATION anchor proof now requires NULL lifecycle source position, present ordered key bounds, and checkpoint position/observation equality only with the immediately preceding anchor.
- DECISION proof now requires a present positive lifecycle source position, absent key bounds, and an exact immediately preceding anchor.
- Rebase lifecycle producers now load and verify the exact current recovery anchor and bind `prior_lifecycle_digest` to that anchor's `anchor_digest`.
- Every supported nonzero lifecycle branch now proves checkpoint `updated_at` equals lifecycle `created_at`.
- Anchor proof now loads an exact revision-zero baseline behind an explicit `F_ANCHOR` cardinality assertion.
- DECISION and KEY_ROTATION audit continuity use complete matching/earlier audit sets, reject duplicate matching heads, load the one matching prior audit exactly, reject any later pre-request audit revision, and otherwise require zero earlier audits plus equality with the baseline anchor digest. These failures are explicitly `F_ANCHOR`.
- Focused candidate-independent AST checks cover the immutable rotation parent constraint, NULL substitution, latest-audit rollback across rotations, missing/duplicate prior-audit evidence, missing baseline, timestamp mismatch, immediate predecessor anchoring, complete replay comparison, and retained R6A branch-local reads.

## Verification

Command run:

`ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`

Result: `All checks passed!`

Per the packet, no pytest, generation, semantic validation, or Git command was run for this correction.

## Unresolved integration needs

Sol must perform generated-contract regeneration, semantic/full deterministic gates, candidate review, and any required independent veto after integrating this bounded correction. This worker makes no acceptance, digest-freeze, commit, push, protected-ref, or baton decision.

## Boundary confirmation

No builder, validator, schema source, generated artifact, other test, plan/design/threat/AER, app/API/Diary/migration file, SQL/DDL, database, source/feed/watcher/listener, provider/network/browser, patient/product data, runtime, credential, command/write, deployment, production, release, Pages, protected ref, branding, or unrelated untracked file was modified. The earlier worker result remains unchanged.

RESULT: candidate_ready
