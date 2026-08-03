# Davida provider-free practice-administration pure read — DeepSeek worker packet

Source head: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-pure-read-context-desk`

Branch: `codex/davida-pure-read-context-desk`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
the EMR4 API Steward skill/checklist completely. Read the accepted Davida
boundary plan/design/threat/contract/schema/closeout and only the named adjacent
runtime sources. Verify exact branch/source and a clean worktree before editing.

## Task

Implement the next bounded Davida descendant as an unmounted, provider-free
pure-read projection and deterministic minimal context desk over authored-
synthetic data. This is backend context preparation outside any probabilistic
cell; it grants Davida no database, auth, route, provider, proposal or apply
authority.

## Permitted reads

- `AGENTS.md`, this packet and accepted seam/Davida artifacts;
- `app/models/tenancy.py`, limited to practice/location/practitioner/user fields;
- `app/schemas/practice.py`, limited to `PractitionerOut`;
- `app/services/practice/practitioner_directory_read.py`;
- existing product-read operational/database-role modules, read-only;
- `app/routers/diary.py`, limited to proving current locations are pure and
  rooms/waiting normalize/commit; do not reuse or edit the router;
- the waiting-room GET boundary in `app/routers/appointments.py`;
- disposable PostgreSQL/Alembic/role helper precedents in the accepted
  product-read acceptance script;
- focused accepted Davida and practitioner-read tests.

Do not perform broad repository discovery or inspect protected/historical
evidence.

## Owned implementation files

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

The acceptance script must write evidence only when root later runs it to:
`orchestration/continuity/davida-provider-free-practice-administration-pure-read/provider-free-in-process-backend-postgres-evidence.json`.
Do not create or commit that evidence now.

Do not edit any other file. Especially forbidden: `AGENTS.md`, accepted
artifacts, `app/main.py`, existing schemas/services/models/routers, shared auth,
GraphQL SDL/runtime, migrations, API Spine, `docs/diary/**`, `docs/branding/**`,
workflows, harness settings, protected evidence and other-agent files.

## Exact projection contract

- Define a strict extra-forbid `ActivePracticeLocationOut` containing only
  `id: UUID` and bounded `name: str`.
- `list_active_location_directory` takes an already-authenticated backend
  `current_user` and DB session; it exposes no role policy and creates no new
  action/resource identifier. Query exactly `PracticeLocation.id` and `.name`,
  scoped to `current_user.practice_id`, `is_active IS TRUE`, ordered by
  `name, id`, fixed maximum 200 under `db.no_autoflush`.
- Do not return/model address, phone, waiting_rooms, active flag, foreign or
  inactive rows, administrative metadata or prototype SDL `displayOrder` (the
  model has no such column). Add no route or GraphQL field.
- The service contains no commit, flush, add, delete or normalization path.

## Exact context-desk contract

- The composer has no SQLAlchemy, model, DB, network, provider or clock import.
  It receives caller-supplied already-authorized exact
  `list[PractitionerOut]`, exact active locations, bounded authored-synthetic
  practice/principal refs, correlation ID, timezone-aware observed time and an
  immutable bounded backend resource-reference registry.
- Replace every internal UUID, including default-location IDs, with a registered
  opaque synthetic resource reference. Missing, duplicate, wrong-kind or
  cross-practice bindings fail closed. Emit no UUID.
- Return strict extra-forbid
  `emr4.davida.practice_administration_context.v1` with
  `data_class=authored_synthetic`, observed/expires exactly two minutes apart,
  deterministic SHA-256 content revision, two fixed `live_api_fact` frames for
  practitioners and locations, exact source/projection/active-only labels, and
  exact blocked sources for diary rooms, diary waiting areas and the
  patient-linked appointment waiting-room queue.
- The authority ceiling is structurally read-only: command, confirmation,
  write, proposal/apply, provider, event actuator and model-to-database authority
  are all literal false. Context frames are minimal and non-authoritative;
  database truth remains authoritative. Repeated fixed inputs produce identical
  frames/revision; unknown fields, naive time and unsupported values fail closed.
- The machine JSON contract/schema must encode exact nested values with required
  fields, `additionalProperties: false` and adversarial mutation tests; do not
  repeat the earlier permissive-schema defect.

## Acceptance harness

- Use one unique allowlisted disposable PostgreSQL database, current Alembic
  head and the existing finite product-read LOGIN/NOLOGIN role builders—no new
  role class or auth policy.
- Seed authored-synthetic current/foreign practices and active/inactive
  practitioners/locations. Execute the exact practitioner precedent plus new
  location service through the product capability session and compose one frame.
- Prove exact fields, tenant isolation, active-only behavior, deterministic
  ordering, empty/bounds behavior, deterministic frame/hash, opaque references,
  no UUID or sensitive residue, SELECT-only SQL, unchanged table counts/hashes
  and session new/dirty/deleted, and direct privilege/write denials.
- Persist only counts, booleans, hashes and safe fixed labels; never DSN,
  database/role names, passwords, IDs, names or raw authority material.
- Dispose sessions/engines, roll back or clean synthetic rows, drop database and
  two roles, and verify absence even on failure.
- Evidence label exactly `provider_free_in_process_backend_postgres`. It is not
  HTTP/browser/provider/product-runtime/usability evidence.

## Verification and commit

Do not run pytest, PostgreSQL or the acceptance script; root holds the serial
database/test lease. You may run Ruff, py_compile, schema validation, direct
pure-function checks that do not load `conftest.py`, AST/static and diff hygiene.
Commit only the ten owned files using explicit `git add` paths. Verify the
cached list is exact and has no `docs/branding/`. Never use `git add -A` or
`git add .`. Do not fetch, merge, rebase, switch or push.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one `DECISION: pass` or `DECISION: revision_required`.
