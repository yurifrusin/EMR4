# Davida provider-free practice-administration pure-read plan

Date: 2026-08-03

Status: provider-free, unmounted, non-executing, authored-synthetic

Reasoning level: bounded DeepSeek V4 Flash/high implementation worker under
Claude Code `--bare`; root GPT Sol owns material architecture, authority and
security decisions.

## Objective

Freeze the next bounded Davida lane descendant of the accepted
`davida_practice_administration_boundary_pass` and `bernie_davida_parallel_seam_pass`:
the provider-free practice-administration pure-read tranche. This packet adds
an unmounted, provider-free pure active-location projection and a deterministic
minimal context desk over authored-synthetic data, while retaining the accepted
active-practitioner projection as the precedent and continuing to block
room/waiting paths until their nominal-read side effects are separated.

This is backend context preparation outside any probabilistic cell. It grants
Davida no database, auth, route, provider, proposal or apply authority. No
route, GraphQL field, model-to-database path, provider call or runtime is
opened, and no database truth is owned by Davida.

## Standing authority

The accepted boundary records Yuri's standing authority for bounded logical
descendants in the Davida Practice Administration lane. The frozen
four-tranche sequence is:

1. pure read projections (this packet);
2. provider-free typed interpretation/proofreading;
3. one bounded proposal path with no apply command;
4. a later human-confirmed command candidate only after the preceding contract
   and risk tier are accepted without a material fork.

Material architecture or product-behaviour forks, new providers/cost/licence,
real patient/clinical/identity data, actual administrative apply authority,
cloud/IAM, deployment, production, release, protected evidence/holdouts,
protected refs and economically preferable manual intervention return to Yuri.

## Scope

### Owned paths

- `app/schemas/practice_administration.py`
- `app/services/practice/active_location_directory_read.py`
- `app/services/practice/practice_administration_context_desk.py`
- `docs/davida-provider-free-practice-administration-pure-read-plan.md`
- `docs/davida-provider-free-practice-administration-pure-read-design.md`
- `docs/security/davida-provider-free-practice-administration-pure-read-threat-model-delta.md`
- `orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.json`
- `orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.schema.json`
- `scripts/davida_provider_free_practice_administration_pure_read_acceptance.py`
- `tests/test_davida_provider_free_practice_administration_pure_read.py`

### Forbidden paths

`AGENTS.md`, accepted artifacts, `app/main.py`, existing schemas/services/models/
routers, shared auth, GraphQL SDL/runtime, migrations, API Spine, `docs/diary/**`,
`docs/branding/**`, workflows, harness settings, protected evidence and
other-agent files. No other file is edited.

## Frozen projection decisions

- `ActivePracticeLocationOut` is a strict extra-forbid schema containing only
  `id: UUID` and a bounded `name: str`. Address, phone, `waiting_rooms`, the
  active flag, foreign/inactive rows, administrative metadata and the prototype
  SDL `displayOrder` (the model has no such column) are never modelled.
- `list_active_location_directory` takes an already-authenticated backend
  `current_user` and a DB session. It exposes no role policy and creates no new
  action/resource identifier. It queries exactly `PracticeLocation.id` and
  `.name`, scoped to `current_user.practice_id` and `is_active IS TRUE`, ordered
  by `name, id`, with a fixed maximum of 200 under `db.no_autoflush`.
- The service has no commit, flush, add, delete or normalization path. No route
  or GraphQL field is added.
- The active-practitioner read `list_practitioner_directory` remains the
  accepted precedent and is retained unchanged.

## Frozen context-desk decisions

- The composer has no SQLAlchemy, model, DB, network or provider import and
  never reads a clock (no `datetime.now`/`time.time`); `observed_at` is always
  caller-supplied and timezone-aware. The `datetime` module is used only as a
  value type and for fixed two-minute expiry arithmetic. It receives
  caller-supplied already-authorized exact `list[PractitionerOut]`, exact active
  locations, bounded authored-synthetic practice/principal refs, a correlation
  ID, a timezone-aware observed time and an immutable bounded backend
  resource-reference registry.
- Every internal UUID, including default-location IDs, is replaced with a
  registered opaque synthetic resource reference. Missing, duplicate, wrong-kind
  and cross-practice bindings fail closed. The frame emits no UUID.
- The frame is strict extra-forbid `emr4.davida.practice_administration_context.v1`
  with `data_class=authored_synthetic`, observed/expires exactly two minutes
  apart, a deterministic SHA-256 content revision, two fixed `live_api_fact`
  frames (practitioners and locations) with exact source/projection/active-only
  labels, and exact blocked sources for diary rooms, diary waiting areas and the
  patient-linked appointment waiting-room queue.
- The authority ceiling is structurally read-only: command, confirmation,
  write, proposal/apply, provider, event actuator and model-to-database
  authority are all literal false. Context frames are minimal and
  non-authoritative; database truth remains authoritative.
- Repeated fixed inputs produce identical frames and revision. Unknown fields,
  naive time and unsupported values fail closed.

## Acceptance harness

- Use one unique allowlisted disposable PostgreSQL database, the current Alembic
  head and the existing finite product-read LOGIN/NOLOGIN role builders — no new
  role class or auth policy.
- Seed authored-synthetic current/foreign practices and active/inactive
  practitioners/locations. Execute the exact practitioner precedent plus the new
  location service through the product capability session and compose one frame.
- Prove exact fields, tenant isolation, active-only behavior, deterministic
  ordering, empty/bounds behavior, deterministic frame/hash, opaque references,
  no UUID or sensitive residue, SELECT-only SQL, unchanged table counts/hashes,
  session new/dirty/deleted, and direct privilege/write denials.
- Persist only counts, booleans, hashes and safe fixed labels; never DSN,
  database/role names, passwords, IDs, names or raw authority material.
- Dispose sessions/engines, roll back or clean synthetic rows, drop the database
  and two roles, and verify absence even on failure.
- Evidence label exactly `provider_free_in_process_backend_postgres`. It is not
  HTTP/browser/provider/product-runtime/usability evidence.

## Acceptance

- `context-contract.json` validates against `context-contract.schema.json`.
- Tests prove the exact strict extra-forbid frame, authority ceiling, blocked
  sources, opaque reference replacement, deterministic revision and fail-closed
  behaviours.
- Tests prove the active-location projection purity (no commit/flush/add/delete/
  normalization) and the bounded exact-field schema.
- Tests include adversarial mutations of the machine contract; every
  authority-bearing or shape-bearing mutation fails schema validation
  (`additionalProperties: false` and exact nested `const` values).
- `git diff --check` passes; `docs/branding/` remains absent from the staged
  index, test scope and intentional patch.
