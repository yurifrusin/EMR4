# B4.1 Davida default-location command runtime — DeepSeek worker packet

Source head: `902040a551668bf8e5a1dd9abaae379224995eec`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-b4-1-default-location`

Branch: `codex/worker-model-required-bureau-b4-1-default-location`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
`docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`, its threat-model
delta, the controlled-recovery development plan, the accepted Davida default-
location command-boundary plan/design/threat/OpenAPI artifacts,
`orchestration/api_spine_adr.md`, `orchestration/api_spine_programme.md`, the API
Steward skill/checklist, and only relevant current authentication, tenancy,
practice, config, migration and API Spine sources. Verify exact branch/source and
a clean worktree before editing.

## Exact task

Implement only plan section 5 and the B4.1 acceptance matrix: one default-off,
authored-synthetic-practice-only, provider-free three-route REST command family
for a single practitioner's default location. Davida is non-authoritative
proposal provenance only. The current authenticated human `Admin` or
`PracticeOwner` is the sole confirmer; map those server enums exactly to
`practice_manager` and `practice_owner` before non-authoritative body assertion
equality, with no aliases or client-selected authority.

All three routes require bounded `Idempotency-Key` and `X-Correlation-Id`; the
header, body session-binding assertion and signed proposal correlation values
must match. Gate the feature and exact practice allowlist before practitioner or
location lookup. Proposal recomputes current active same-practice resources and
returns a signed self-contained maximum-120-second proposal without a database
write. Use a dedicated server-only B4 command secret and fail closed if absent
or invalid.

The confirmation-evidence route verifies proposal/path/body/hash/session/current
state and inserts one opaque server-held one-use reference bound to proposal and
canonical attestation hashes. Exact concurrent retry may return the same active
reference; changed payload conflicts; expired or consumed evidence cannot renew
the old proposal.

Confirmation durably claims hashed idempotency, locks the exact practice-scoped
practitioner and evidence row, reauthorizes, verifies proposal/evidence/hash/
expiry/version/before-state and active same-practice target location, rejects
no-op/stale/replay, updates `default_location_id`, increments
`aggregate_version` once, consumes evidence, appends one immutable audit and one
unpublished patient-free outbox row, stores the bounded receipt, commits once
and freshly reloads deterministic state. The event is exactly
`practice.practitioner_default_location_changed` with schema
`practice.practitioner_default_location_changed.v1`, the five plan payload
fields and fixed reason code. Enable and force exact practice RLS; make audit and
outbox append-only. Add no publisher/consumer.

## Owned paths

- `app/config.py`
- `app/main.py`
- `app/models/tenancy.py`
- `app/models/practice_administration_commands.py` (new)
- `app/schemas/practice_administration_default_location_command.py` (new)
- `app/services/practice/practice_administration_default_location_command.py`
  (new)
- `app/routers/practice_administration.py` (new)
- `alembic/versions/v1w2x3y4z5b6_add_b4_default_location_runtime.py` (new
  provisional descendant of exact `u0v1w2x3y4z5`; Sol owns final cross-lane
  chain)
- `docs/api-spine/openapi/practice-administration-default-location-commands.yaml`
- `tests/test_model_required_bureau_b4_1_default_location_runtime.py` (new)

Do not edit any other path. In particular do not edit `AGENTS.md`, the frozen
plan/threat/review artifacts, the accepted dry-run schema/service, appointment/
Diary/event sources, another migration, GraphQL, provider configuration,
deployment/workflows, Continuity/Compass global maps, `docs/branding/**`,
protected/historical evidence or the other worker lane.

## Required tests in the owned test file

Cover zero-write proposal, expiry/signature/current-state binding, default-off
and non-allowlisted rejection before lookup, both exact allowed roles and every
other role, exact server role mapping/body mismatch, required bounded headers
and correlation equality, missing/invalid secret fail-closed, same-practice
active resource checks, no-op/stale version/before-state rejection, attestation
exact retry/changed payload/concurrent behavior/expiry, same-key replay,
changed-fingerprint conflict, in-progress denial, different-key evidence replay,
concurrent single winner, aggregate version increment, exact audit/outbox and
fresh readback, forced RLS/cross-practice denial, append-only enforcement,
rollback at every persisted member, unpublished event, OpenAPI three-route
parity and one Alembic head. Assert no raw idempotency/session secret, patient
field, provider output or free text is stored and zero product-provider calls.

## Mechanics and forbidden claims

Use `apply_patch` only. Do not run PostgreSQL pytest or the acceptance script;
Sol holds the shared serial database/test lease. You may run Ruff, py_compile,
AST/static checks, YAML parsing and `git diff --check`. Stage only the owned
paths by explicit pathname, verify no `docs/branding/` path is cached, and
commit once to the worker branch. Do not fetch, merge, rebase, switch, push,
deploy or move protected refs.

This is local/provider-free/authored-synthetic command implementation only. No
patient, clinical, product-derived, participant, protected or production data;
no product-provider call, GraphQL mutation, autonomous action, external outbox
delivery, deployment, release, Pages or protected-ref authority.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one `DECISION: pass` or `DECISION: revision_required`.
