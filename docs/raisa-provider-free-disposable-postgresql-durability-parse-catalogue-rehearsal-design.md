# Provider-free disposable PostgreSQL durability parse/catalogue rehearsal design

Date: 2026-08-07

Status: candidate companion design; no runtime authority before plan admission

## Components

The tranche has four deterministic components:

1. `RehearsalContractV1` binds the parent bytes, exact Docker profile, fixed
   command grammar, catalogue projections, claim boundary and cleanup rules.
2. `SyntheticPrerequisiteContractV1` declares the four empty application table
   shapes needed only for dependency resolution.
3. `DisposablePostgresRehearsal` owns one container lifecycle and streams fixed
   SQL/readback scripts through `docker.exe` using argument-vector subprocesses.
4. `RehearsalEvidenceV1` records bounded stage outcomes, canonical catalogue
   digests, rollback proof and exact cleanup proof.

The implementation is standard-library-only. It imports no ORM, database
driver, HTTP client, cloud SDK, provider harness or application service. The
Docker CLI is the sole process boundary.

## Lifecycle state machine

The only legal forward states are:

`parent_verified -> environment_verified -> container_created ->
container_owned -> postgres_ready -> prerequisites_installed ->
artifact_admitted -> catalogue_matched -> rollback_case_matched ->
cleanup_verified -> passed`

Any failure after creation enters `cleanup_pending`. Only a reverified exact
ID may enter `cleanup_authorised`. Successful removal and exact-ID absence
produce `cleanup_verified`. If ownership verification fails, the terminal state
is `cleanup_ownership_unverified`; no deletion command is issued.

The evidence records every entered state once and rejects skipped, repeated or
out-of-order transitions. A pass is impossible without cleanup verification.

## Closed Docker command grammar

Each subprocess call is built from an enum-backed operation, not a free-form
list. Permitted operations are exact-image inspect, exact-name absence inspect,
bounded `run --detach`, exact-ID inspect, exact-ID `exec -i` for one fixed
`pg_isready` or `psql` operation, exact-ID removal after ownership proof, and
exact-ID absence inspect.

The create/run vector fixes image, name, labels, no-pull, no-network, tmpfs,
resource bounds, restart disabled and authored-synthetic initialization
variables. Tests reject `pull`, `build`, `login`, `compose`, `ps`, `images`,
`system`, `prune`, globbing, shell metacharacters, port flags, bind/volume
mounts, Docker socket access, host networking, privileged mode and caller
arguments.

The image preflight uses exact-reference inspect only. The harness compares the
created container's immutable image ID with that preflight result, so tag drift
between preflight and creation fails before SQL.

## SQL transport and transaction boundaries

SQL is supplied as bytes over subprocess standard input. No workspace path is
made visible inside the container. Every `psql` call fixes database, user,
Unix-socket host, `--no-psqlrc`, `--quiet`, `ON_ERROR_STOP=1` and output mode.

The prerequisite transaction and canonical artifact transaction are separate.
This makes the synthetic dependency shapes available while keeping the fabric
installation atomic. The accepted artifact is decoded as UTF-8, permits only
working-tree CRLF-to-LF normalization, and must then match the manifest's
canonical hash and byte count. Those canonical bytes are streamed byte-for-byte
with no wrapper edit; psql supplies its outer single transaction. The negative
case uses a fresh synthetic database and an in-memory invalid suffix after the
canonical bytes, then verifies absence of fabric objects and accepted roles
after rollback.

The harness never invokes a function with `SELECT`/`CALL`, never writes an
application row and never disables a trigger or policy. Catalogue queries set
the transaction read-only before selecting `pg_catalog` facts.

## Catalogue normalization

Every query has a fixed identifier and exact ordered columns. Results are
normalized as UTF-8 JSON scalars and sorted only by contract-declared stable
keys. Expressions returned by PostgreSQL are normalized using PostgreSQL's own
identity/deparse functions named in the contract; the harness does not invent
semantic equivalence.

Comparisons are exact for object identities, counts, owners, role attributes,
RLS flags, policy roles/commands/expressions, constraint/index definitions,
function identity arguments and attributes, `proconfig`, trigger properties,
ACL facts and dependency targets. The evidence stores closed expected/observed
counts and SHA-256 digests plus only bounded mismatch pointers. It does not
store unrestricted catalogue dumps.

## Synthetic prerequisites

Prerequisite SQL is rendered from the closed contract, not copied from the
application ORM or inferred from a live database. It creates exactly the four
`public` tables and minimum keys. All tables are empty and remain owned by the
authored-synthetic initialization role. The harness records relation owner and
row-count facts immediately before and after artifact admission.

The prerequisite contract is deliberately not a claim that these shapes are a
complete application migration. It proves only that every external reference
used by the accepted durability artifact can resolve against the accepted
column/type catalogue.

## Resource and failure containment

Container startup, readiness, each SQL phase, catalogue readback, removal and
total execution have explicit deadlines. Output capture is byte-capped. On
overflow, timeout, client failure, server error or unexpected state, the
harness records a bounded value-free failure and enters cleanup.

The container receives no host port, network, bind, named volume or Docker
socket. PGDATA is tmpfs. Restart is disabled. The harness neither discovers nor
operates on unrelated Docker state. Cleanup receives only the ID returned by
the successful owned `run` operation and independently proves its name, labels,
image and containment configuration.

## Evidence and repeatability

Runtime-specific nonce, container ID, timestamps and timing are evidence, not
canonical acceptance inputs. Canonical evidence fields comprise parent hashes,
contract hashes, image reference and ID, server major, exact configuration
facts, normalized catalogue counts/digests, negative rollback outcome and
cleanup outcome. A verifier independently recomputes every deterministic hash.

If the exact local image is absent, no pass evidence is emitted. If a repair is
needed, the failed evidence remains immutable, a new owned run is created and
the accepted evidence names the full attempt lineage.

## Non-authority statement

This design adds no migration, operational database, durable data, credential,
source/watcher/listener, application route, API operation, Diary behavior,
patient/product data, provider product call, deployment, production, release,
Pages rebuild or protected-ref authority.
