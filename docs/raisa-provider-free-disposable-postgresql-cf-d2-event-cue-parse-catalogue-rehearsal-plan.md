# Provider-free disposable PostgreSQL CF-D2 event and cue parse/catalogue rehearsal plan

Date: 2026-08-13

Timestamp: 2026-08-13T19:21:56+10:00 (Australia/Brisbane)

Status: `frozen_for_exact_artifact_disposable_postgresql_16_execution`

Planning baseline: `ad847eda9beff8317aa83779d7ca36a7b95b3ebd`

Accepted inert-DDL source: `cd890647d327a3d9bf4f60e5e1d6f9a1924bab29`

Target result: `raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_pass`

Reasoning level: High; bounded mechanical execution against an already frozen
artifact, with no new architecture or authority decision.

## Objective

Ask one isolated, newly created PostgreSQL 16 server exactly one narrow
question: do the accepted `.sql.inert` bytes parse and create the exact
catalogue shape already frozen by the CF-D2 representation and lowering
contracts?

The server and data directory are owned by this rehearsal, contain no rows,
have no network, and are destroyed at the end. This is database
representability evidence only. It is not an Alembic migration, an application
database, durable storage, a watcher, a source connection or runtime wiring.

Events and cues remain acceleration hints. Nothing in this rehearsal makes
them Diary truth, Context Frames, confirmation evidence, command authority or
command receipts. A display still requires a fresh authorised source read and
every consequential command still rechecks current authority and source truth.

## Exact source bindings

The fixed harness reads only these exact repository inputs:

| SHA-256 | Path |
|---|---|
| `3eebbe132b195ccab2f00283ad20f04c521fa6116bb30d0f38ab49158db1ebd6` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/event-cue-schema.sql.inert` |
| `ca66a12388b9677dcd9f5c3f13e4ca680d130cd001c321bd5dfa7b0e30497ca8` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/inert-ddl-manifest.json` |
| `736d3eab20ae6563a0f23801bb8ef1e4d7a6169648ea49e1607c4baac75dd8d5` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering/inert-ddl-contract.json` |
| `ff72cb2b6458193fb723b19209ac0ca487d3fdda5846d43ccdfafb6986957f64` | `orchestration/continuity/raisa-provider-free-unmounted-cf-d2-event-cue-representation-architecture/representation-contract.json` |
| `95b6005811817937d34093775ac17c82d6100626e15ab75fa252177995675c62` | `docs/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering-closeout.md` |
| `41065ca2ae4754eb28ca6d62ec4895009d0ae11d54d9f05b8c0c03a18acf5b2b` | `orchestration/agent_inbox/codex/raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-sol-acceptance.md` |

The SQL artifact is streamed byte-for-byte through standard input. The harness
cannot accept a caller-selected SQL string, path, database URL, image,
container, output or catalogue query.

## Owned environment

- Host executable: only the locally resolved `docker.exe`.
- Image: the already cached `postgres:16-bookworm` at exact image ID and repo
  digest frozen in the rehearsal contract. Local inspection precedes create;
  `--pull=never` forbids registry access.
- Container: a random name beneath one fixed prefix plus exact harness and
  cleanup-nonce labels. Only its captured full ID may be inspected, executed
  within or removed.
- Network: `--network=none`, no published ports, no network join and no host
  database URL.
- Storage: one container-local tmpfs at `/var/lib/postgresql/data`; no bind,
  named volume, workspace or Docker-socket mount.
- Bounds: one CPU, 512 MiB memory, 128 processes, no restart, 90-second startup,
  30-second commands and 300-second total intent.
- Bootstrap values: fixed authored-synthetic database/user/password values
  used only inside the owned container and never treated as credentials.
- SQL transport: `docker exec -i` to in-container `psql` over its local Unix
  socket, with argument vectors and `shell=False`.

The harness never lists or prunes containers, pulls or builds images, removes
an image/volume/network, starts Docker Desktop, opens a socket, or touches an
object whose exact ownership profile cannot be reverified.

## Admission sequence

1. Verify the closed rehearsal contract, at least 64 independent hostile
   contract mutations, all exact source hashes and unchanged canonical bytes.
2. Resolve Docker, inspect the exact cached image, and fail
   `environment_unavailable` without fallback if any dependency is absent.
3. Create one networkless tmpfs container with the exact frozen profile and
   capture its full ID.
4. Reinspect that ID and require exact name, image, labels, environment,
   network, tmpfs, memory, CPU, process and restart properties.
5. Require three consecutive authenticated readiness observations and
   `server_version_num` major 16.
6. Stream the exact 12,022 artifact bytes through `psql --file=-`,
   `ON_ERROR_STOP=1` and `--single-transaction`. The transaction wrapper is
   harness containment only and proves none of the five CF-D2 protocols.
7. Execute fixed read-only `pg_catalog` projections and admit the exact schema,
   domain, table, column, constraint, reference and absence facts.
8. Prove all seven relations contain zero rows.
9. Reverify ownership, remove only the captured ID in `finally`, and prove its
   exact absence.

## Exact catalogue acceptance

The fixed projection must prove:

- one target schema named `emr4_context_fabric_cue`;
- exactly three domains over `text`, `text` and `bigint`, with the three named,
  validated domain checks;
- exactly seven ordinary tables in accepted order and fifty columns in exact
  table/ordinal/name/type/nullability order, with no defaults;
- exactly seven primary keys, three unique keys, eighteen table checks and
  seven foreign keys, all named, validated and bound to the exact table and
  ordered column lists;
- only `fk_terminal_receipt_obligation` is deferrable and initially deferred;
- the other six foreign keys are not deferrable and not initially deferred;
- zero target-schema functions, procedures, triggers, views, materialized
  views, sequences, policies, non-internal rules or row-security tables;
- no object ACL was explicitly added; and
- zero rows in every target table.

Constraint definitions are retained only as canonical digests in evidence.
Because the exact source bytes are hash-bound and submitted unchanged, the
catalogue proof need not reverse-engineer PostgreSQL's normalized expression
printer to restate the already frozen check text.

## Acceptance

- Fresh five-source receipt and active-operation latch pass.
- Contract and evidence schemas validate as whole documents.
- At least 64 hostile contract mutations fail closed.
- Exact source hashes and artifact byte count pass before Docker contact.
- Docker/image/profile/readiness admission is exact and offline.
- The exact artifact installs atomically and the exact catalogue projection
  passes.
- All seven row counts are zero.
- Cleanup proves exact captured-ID absence.
- Focused static/hostile tests, parent lineage, Ruff, canonical fast profile,
  compile, JavaScript syntax and Git whitespace pass serially where required.
- Protected refs and every unrelated untracked file remain unchanged.

Evidence is labelled
`authored_synthetic_provider_free_disposable_postgresql_16_parse_catalogue`.
It proves parse and catalogue shape only.

## Recovery

Missing Docker, daemon or exact cached image is a terminal
`environment_unavailable` outcome without pull or fallback. A mechanical
harness, SQL admission or catalogue-projection defect may receive bounded
evidence-backed repair inside this exact envelope using a fresh owned
container. If cleanup ownership cannot be proved, the harness refuses removal
and requires human attention with the exact captured ID recorded locally.

## Next descendant

If this tranche passes, the next dependency-satisfied candidate is the
narrowest provider-free disposable PostgreSQL behavior/transaction rehearsal
for the five already frozen protocols: terminal admission, pending
coalescing, contiguous checkpoint advance, dispatch recording and
reconciliation. Its exact scenarios must be derived and frozen separately.
This plan grants that descendant no implementation authority in advance.

## Closed surfaces

No protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient client or identity, existing database or source, watcher/
listener/worker runtime, durable persistence or operational retention,
transaction-protocol behavior claim, concurrency, restart, unknown commit,
provider/ADC, credential/IAM/external network, application route, tool,
command/write, deployment, production, release, Pages or protected-ref action
is opened. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.
