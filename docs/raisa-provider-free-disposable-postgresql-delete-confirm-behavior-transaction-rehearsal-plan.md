# Provider-free disposable PostgreSQL delete-confirm behavior/transaction rehearsal plan

Date: 2026-08-16

Timestamp: 2026-08-16T11:52:20+10:00 (Australia/Brisbane)

Source HEAD: `87f352aa1d2a9bc9366e20032f6c9a2fd1b6fe67`

Status: `frozen_for_tier_2_provider_free_disposable_postgresql_execution`

Reasoning level: material database authority and transaction execution / Extra High

Risk classification: Tier 2 (`database_runtime`,
`authority_or_security_contract`, `migration_execution`, `executable_tool`)

## Purpose

Exercise the exact accepted delete-confirm database scaffold and exact unmounted
`delete_confirm_locked_transaction` seam in one newly owned disposable
PostgreSQL 16 runtime. The rehearsal asks two bounded questions:

1. do PostgreSQL's generation and grant triggers make current authority
   immutable, default-denying, revocable and overflow-safe; and
2. does the unmounted seam preserve authority-first lock order, private receipt
   and attributable audit integrity, byte-exact replay, cumulative timeout and
   all-or-nothing rollback for one serial cancellation command?

Only fixed authored-synthetic fixture rows are admitted. This is not product
capability provisioning, a mounted route or a product command. It excludes
concurrency, restart and unknown-commit behavior.

## API Spine classification

This is private evidence beneath the dedicated REST/OpenAPI command
`confirmAppointmentDeleteProposal`. Public OpenAPI, routers and response schemas
remain byte-for-byte unchanged. GraphQL remains read-only. Events remain
non-authoritative acceleration hints. The stored canonical response bytes are
private command-receipt evidence and never an event, read model or public
delivery contract.

## Admission and baseline

The fresh preplanning state and receipt are
`orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-preplanning-runtime-state.json`
and
`orchestration/agent_inbox/codex/raisa-delete-confirm-behavior-transaction-preplanning-receipt.json`.
The receipt passes with all five named authority sources and the in-progress
operation latch.

Before the first semantic edit, the canonical fast profile passed at exact HEAD
`87f352aa1d2a9bc9366e20032f6c9a2fd1b6fe67`: Ruff, maintained compilation,
196 tests, Diary syntax and whitespace. The baseline record is
`orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/baseline-fast-profile.json`.

At admission, task HEAD and origin task were exact `87f352aa1d2a9bc9366e20032f6c9a2fd1b6fe67`.
Local/origin `master` and `handoff/current` were exact protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. The tracked tree was clean and
635 untracked paths, including `docs/branding/`, were preserved.

## Exact source bindings

Only these non-protected authority and implementation inputs may be bound by the
closed rehearsal contract:

| SHA-256 | File |
|---|---|
| `4881910f3fa3fd133f753ccb43f20417e38dc3cf1b6eeac740904ed16708a53e` | `docs/raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-parse-catalogue-rehearsal-closeout.md` |
| `07970f0dac2c68abe0a537c3ee1855192eef1e02a61773fc4ca0cd1594204def` | `orchestration/agent_inbox/codex/raisa-delete-confirm-scaffold-parse-catalogue-sol-acceptance.md` |
| `34e9c7f955aef327e6b2da863e7d15b6e457c4ec2c7c0c658b15c93c426f32c4` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence.json` |
| `41abded0e169f339ea581a90aba061b4896e322dad2962e252ef0c069a0439e4` | `scripts/raisa_provider_free_disposable_postgresql_delete_confirm_scaffold_parse_catalogue_rehearsal.py` |
| `2970edf7c04ce0988c0904c8cc02bcd2176fdafccc5b1d745ce9240ca4f8f007` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-scaffold-parse-catalogue-rehearsal/rehearsal-contract.json` |
| `f6e75c7428dc5c1327166bc0e900c2804f3201ea1b32cd5577d1f8134b16c2a8` | `docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-plan.md` |
| `4d4ecc83fdb9b9e90067714f4827be6bc007ddd183bc66b0cd95aa207d475f22` | `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.json` |
| `8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533` | `app/services/appointment_delete_physical.py` |
| `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` | `app/models/tenancy.py` |
| `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` | `app/models/appointments.py` |
| `e6542c960a9378cf7c1c3c22dd876a1c9f242b68047a180f9f383c1c62d348bb` | `alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py` |
| `65b88f86e7fa2f1fbc43e381eb2c4afcfddf22ff0ad616e60438637137db5280` | `docs/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal-plan.md` |
| `875afd5bdfcac9e8cdbc5deb000645c638b68d1eb2239d3cd55f130366c08bd9` | `scripts/raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal.py` |
| `bdc848e2033715eb110f3d55425e06894abbc3a492c0a35fea0a2daf2c55d19b` | `orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-behavior-transaction-rehearsal/rehearsal-contract.json` |
| `c5493c14efd92b3d3fc3d8a0ef33d3e3a266fa1d0961ad90ebbc37e4b4065a3a` | `docs/api-spine/openapi/appointment-commands.yaml` |
| `a4bc7f92d1caecbd0b421cd40438d64916a7945197e02d2f8b9232d2162c2284` | `orchestration/harness_settings/risk_weighted_workflow.yaml` |

The accepted status-confirm harness is reusable only as exact containment,
relay and transaction-fixture support. Its status semantics are not imported as
delete-confirm evidence. Reusing its fixed helpers avoids another independent
Docker lifecycle implementation without weakening the delete-specific contract.

## Exact owned artifacts

The implementation worker may create only:

- `orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/rehearsal-contract.json`;
- its whole-document JSON schema;
- one minimized behavior/transaction evidence schema and evidence document;
- `scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py`; and
- `tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal_plan.py`.

Sol alone owns this plan, its threat-model delta, receipts, latch, semantic
freeze, review packets, error register, closeout, acceptance, Continuity,
Compass, baton and Yuri summary. Existing migration, model, service, API, route,
UI and prior harness files must remain unchanged. A discovered defect in those
bound sources fails closed into an explicit Sol recovery revision; it is not
silently repaired by the worker.

## Disposable runtime and fixed relay

- Use the exact repository interpreter and locally resolved `docker.exe`.
- Use only the already cached `postgres:16-bookworm` image with `--pull=never`.
- Create one unique labelled Docker `--internal` network and one unique labelled
  container attached only to it. Publish no Docker port.
- Store PostgreSQL data only in container-local tmpfs; allow no bind, named
  volume, workspace or Docker-socket mount.
- Hold one CPU, 512 MiB memory, 128 processes, no restart, 90-second startup,
  30-second command and 360-second total bounds.
- After exact-ID inspection, start one in-process IPv4 relay on an
  operating-system-selected `127.0.0.1` port. Each connection may invoke only
  the captured container ID with argv, `shell=False`, and the exact accepted
  literal container-side `/dev/tcp/127.0.0.1/5432` relay command.
- Build the SQLAlchemy URL internally from fixed synthetic credentials and the
  selected loopback port. Retain neither URL nor credentials in evidence.

No caller selects a Docker target, database URL, host, port, command or SQL.
The harness never lists, pulls, builds, logs in, prunes or removes an object it
did not create and reverify.

## Minimum transaction-faithful schema and installation

Bootstrap only the mapped columns and correlation constraints needed by
`Practice`, `User`, `Appointment`, `AppointmentAuditLog` and
`AppointmentCommandIdempotency`, plus Alembic predecessor
`w2x3y4z5a6b7`. All person-bearing appointment fields remain null and all
opaque identifiers/text are repository-authored fixtures.

Generate only offline range `w2x3y4z5a6b7:x3y4z5a6b7c8`, strip its exact outer
transaction wrapper, and install the otherwise unchanged body atomically with
`ON_ERROR_STOP=1` and `--single-transaction`. Then add only the already-bound
command/audit correlation constraints required for the ORM write set. Exact
head, trigger inventory and selected constraints must be read back before any
behavior case.

Fixture DML may insert or mutate only the fixed synthetic rows required by the
named cases. It is not a product provisioning path and leaves no durable grant.

## Frozen authority/trigger case groups

Each group starts in a separately keyed synthetic partition and ends with exact
generation/grant counts or a before/after digest:

| ID | Required behavior |
|---|---|
| `AUTH-S01` | user insert forces generation one even when another positive generation is submitted; a direct generation-only update is ignored |
| `AUTH-S02` | role, active-state and practice-membership changes each advance exactly once in isolated subcases; unrelated updates do not advance |
| `AUTH-S03` | exact `appointment.cancel.confirm` insert advances the parent once; row absence before insert is default denial |
| `AUTH-S04` | duplicate exact insert including `ON CONFLICT DO NOTHING` leaves the row and generation unchanged |
| `AUTH-S05` | exact grant delete advances the parent once and restores default denial |
| `AUTH-S06` | grant update is rejected; original row and generation survive unchanged |
| `AUTH-S07` | unknown capability and missing-parent inserts fail; no grant or generation change survives |
| `AUTH-S08` | qualifying user change and grant change at BIGINT maximum fail with no wrap or partial effect |
| `AUTH-S09` | reassignment by delete then insert advances each affected parent exactly once and never mutates capability identity in place |

These prove only serial trigger effects. They do not claim contention, event
delivery, watcher behavior or administrative provisioning safety.

## Frozen transaction case groups

Every invocation uses a new SQLAlchemy `Session`, exact imported
`delete_confirm_locked_transaction`, `READ COMMITTED`, the fixed 2000 ms
cumulative monotonic deadline and no savepoint, retry, `NOWAIT`, `SKIP LOCKED`
or advisory lock.

| ID | Required behavior |
|---|---|
| `TX-S01` | clean `new_command` stages one `Cancelled` appointment transition, one attributable delete audit v1 and one complete private receipt v1, then commits exactly once |
| `TX-S02` | discarded response followed by exact retry releases byte-identical stored canonical bytes with no second appointment, audit or receipt effect |
| `TX-S03` | same key with changed request or session binding is `conflict` and releases no stored bytes |
| `TX-S04` | in-progress, legacy-completed and corrupt-hash rows return their exact non-replay classifications without byte disclosure |
| `TX-S05` | inactive/missing user or absent practice-scoped appointment returns the common target-unavailable outcome before idempotency access |
| `TX-S06` | missing exact grant, stale signed generation or role mismatch returns authority-revoked before idempotency access; role membership alone never grants |
| `TX-S07` | fixed same-transaction revocation immediately before the second internal check rolls back a newly inserted claim and releases nothing |
| `TX-S08` | replay after generation or grant revocation releases no stored bytes and creates no effect |
| `TX-S09` | empty, appointment-only, appointment-plus-audit and cross-artifact-mismatched write sets each raise `DeleteConfirmScaffoldIncomplete` and restore their exact before digest |
| `TX-S10` | a fixed harness abort after a complete write set rolls back appointment, audit and receipt together |
| `TX-S11` | a controlled monotonic clock exhausts the single cumulative deadline before a later blocking access; the exact wait exception occurs and no candidate effect survives |

For `TX-S01`, a value-free SQLAlchemy observer must prove the exact order:

1. user authority fence `FOR SHARE`;
2. practice-scoped appointment `FOR UPDATE`;
3. first exact grant/current-authority query;
4. idempotency `FOR UPDATE` select before insert;
5. only-if-absent target-bound `INSERT ... ON CONFLICT DO NOTHING`;
6. winning idempotency row `FOR UPDATE`;
7. second exact grant/current-authority query; and
8. classification before any staged mutation.

The harness stages the clean write set only after `new_command`. It refreshes
the trigger-owned adjacent appointment version, constructs the exact six-field
canonical response, stores its lowercase SHA-256 and JSON equivalent, and
correlates receipt and audit in both directions. Durable evidence stores only
statement-class tokens, never raw SQL or values.

## Evidence minimization and cleanup

Evidence may retain only source and environment digests, containment booleans,
fixed case/subcase IDs, decision or exception labels, counts, state versions,
value-free statement tokens, canonical-byte digests and cleanup outcomes. It
must not contain raw SQL, URL, password, session binding, response body, log,
unrestricted row, email-like fixture, runtime ID or provider data.

Cleanup runs in `finally`: stop the relay, dispose the engine, re-inspect the
captured container ID and require exact ID/name/image/labels/network/tmpfs/
bounds/no-port/no-other-mount identity before removing only that ID and proving
absence; then re-inspect the captured network ID, require exact empty owned
internal-network identity before removing only that ID and proving absence.
Ownership ambiguity refuses destructive cleanup and requires human attention.

## Risk-weighted gate budget and parallelism

- The one canonical pre-edit baseline already passed and is not repeated for
  receipt or closeout-only changes.
- DeepSeek V4 Flash/high is reserved for the closed contract/schema,
  fixed-path harness and focused tests after this semantic plan is committed.
- Sol performs source admission, occupied execution, recovery, integration and
  acceptance. The stateful runtime is serial.
- Gemini 3.7 Flash/high supplies exactly one final Tier-2 veto after deterministic
  admission and occupied evidence pass.
- Native subagents are declined because another implementation/review lane would
  duplicate those roles and add shared-state overhead.

The candidate receives one semantic freeze recording exact HEAD/tree,
semantic-binding digest, toolchain digest and focused results. Post-freeze
semantic repairs rerun the affected focused gates and one canonical final
profile; metadata changes run only their targeted gates. No stacked reviewer or
intermediate external review is admitted.

Yuri's observation that the reformed workflow feels smoother is recorded as an
early qualitative signal. This tranche will compare planned versus actual
worker use and recovery cycles, but one or two tranches cannot prove a general
throughput improvement.

## Acceptance

Pass only if:

1. the five-source receipt and every exact source binding pass;
2. whole-document contract/evidence schemas pass and hostile semantic mutations
   cover every named threat rather than an arbitrary numeric quota;
3. exact image/network/container/relay/readiness/install/cleanup containment
   passes;
4. all nine authority groups and eleven transaction groups reproduce their
   exact outcomes against the imported migration, models and service seam;
5. clean commit proves one adjacent appointment mutation, attributable audit and
   complete private receipt, and exact replay is byte-identical with no effect;
6. every denial, timeout and rollback partition retains or restores its frozen
   digest and releases no forbidden bytes;
7. the success trace proves the frozen order and both current-authority checks;
8. focused contract/harness/plan/API Spine/lineage tests, Ruff, compilation,
   whitespace and the one required canonical final profile pass;
9. exactly one fresh Gemini 3.7 Flash/high exact-candidate veto passes with an
   unchanged review worktree; and
10. protected refs and every unrelated untracked path remain unchanged.

## Forbidden surfaces

No existing or product database, durable storage, product capability
provisioning, mounted/called route, public API/GraphQL/UI edit, real product
command, concurrency, restart, unknown commit, patient/clinical/real-person/
product/historical-diary/protected data, provider/ADC/credential/IAM/browser,
external network, watcher/event authority, deployment, production, release,
Pages or protected-ref movement. Preserve `docs/branding/` and every unrelated
untracked file. Stage explicit paths only.

## Recovery and next candidate

A harness-only mechanical defect may receive one bounded evidence-led repair
inside the exact owned paths. A contradiction in the bound migration, model or
service source stops into a Sol-owned plan revision and preserves the failed
attempt; no worker broadening is allowed. Environment absence returns
`environment_unavailable` without fallback. Cleanup ownership uncertainty stops
all removal outside the exact verified IDs.

If this passes, the next narrow dependency-satisfied candidate is a provider-free
read-only delete-confirm route-convergence admission review. It may inspect only
the exact route/kernel/adapter gap; it may not edit, mount or call a route, open
product data, or claim UI/runtime readiness.
