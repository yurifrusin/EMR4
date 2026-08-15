# Bounded DeepSeek work packet — delete-confirm physical-design artifacts

Date: 2026-08-15

Timestamp: 2026-08-15T15:32:00+10:00 (Australia/Brisbane)

Bound source commit: `829491fa54b110168333e0fcc4fdf594e1317c30`

Worker: DeepSeek V4 Flash / high through Claude Code `--bare`

## Rehydrate and bind

Read `AGENTS.md` completely, then read these exact controlling files completely:

- `docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-plan.md`
- `docs/security/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-threat-model-delta.md`
- `orchestration/agent_inbox/codex/raisa-reception-one-delete-confirm-physical-design-architecture-preplanning-receipt.json`

Verify the exact worktree root, named branch, clean state and bound source commit
before editing. The plan is semantically frozen. Do not reinterpret, simplify or
extend it. If two frozen statements genuinely conflict, stop with
`revision_required`; do not choose.

## Exact owned paths

Create and commit exactly these five files and no others:

1. `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.json`
2. `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.schema.json`
3. `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/provider-free-physical-design-evidence.json`
4. `scripts/raisa_provider_free_unmounted_delete_confirm_physical_design_architecture.py`
5. `tests/test_raisa_provider_free_unmounted_delete_confirm_physical_design_architecture.py`

Do not edit the plan, threat delta, AGENTS, application, model, schema, service,
router, OpenAPI, migration, configuration or any other file.

## Mechanical implementation contract

Encode every frozen decision in the plan as closed JSON with
`additionalProperties: false` throughout all object schemas. The validator must
use only Python standard-library deterministic logic plus `jsonschema` for
schema admission if already available; it must not import any `app`, Alembic,
database, network, cloud or provider module.

The contract and evidence must cover, without semantic invention:

- exact twenty source paths and SHA-256 values;
- product `users` authority generation and the closed normalized
  `user_capability_grants` relation;
- exact capabilities `appointment.cancel.confirm` and `appointment.read`;
- database-owned generation and fail-closed migration/provisioning order;
- existing appointment state version and exact mandatory Cancelled reason set;
- family-qualified private receipt v1 with the one additive authority generation;
- exact six-field canonical response order and byte/hash rules;
- versioned attributable audit with separate human warnings/internal evidence;
- READ COMMITTED, one cumulative 2000 ms budget and exact ordered lock/check,
  classification, effect and delivery sequence;
- separately authorised fresh readback that never proves commit;
- raw compatibility/status/model/event/channel non-authority;
- `implementation_authorized: false` and every forbidden surface; and
- DeepSeek worker/no acceptance authority plus frozen Gemini 3.6 veto allocation.

The evidence must be authored-synthetic, minimized and provider-free. The
validator must admit the frozen evidence, verify all source hashes, and expose a
testable mutation function or equivalent closed checks. Tests must demonstrate
at least sixty distinct hostile mutations rejected, including every hostile
family named by the plan. Do not pad the count with duplicate encodings of one
mutation. The script must have no executable DDL, SQL, database connection,
subprocess, shell, filesystem mutation, network, credential or runtime-control
path.

## Verification and handback

Run only:

- JSON parse and Draft 2020-12 schema validation;
- focused pytest for the one owned test file;
- Ruff over the two owned Python files;
- `python -m py_compile` over the two owned Python files;
- `git diff --check` and exact owned-path/status checks.

Use explicit-path staging only. Never use `git add .` or `git add -A`. Commit
only the five owned files with message:

`Implement delete-confirm physical design evidence`

Return the exact commit, changed paths, test counts, hostile mutation count,
source-hash result, clean worktree status and one terminal
`DECISION: pass|revision_required`. You have no acceptance, integration, baton,
protected-ref, push, provider, product, deployment or release authority.
