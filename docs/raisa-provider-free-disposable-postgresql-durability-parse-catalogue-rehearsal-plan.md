# Provider-free disposable PostgreSQL durability parse/catalogue rehearsal plan

Date: 2026-08-07

Status: bounded composite-dependency recovery candidate; corrected parent
artifact source is `4911cba926cb69b4f7f945a77d744ff07ab2d3d4`,
with fresh exact-HEAD descendant veto required before another runtime attempt

Parent result:
`raisa_provider_free_unmounted_durability_inert_ddl_rehearsal_pass`

Accepted corrected parent source HEAD:
`4911cba926cb69b4f7f945a77d744ff07ab2d3d4`

Planning baseline HEAD:
`253230a25ab172b90bc5f44772670c7df89b3052`

Parent inert SQL artifact:
`orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`

Parent inert SQL SHA-256:
`sha256:5e23fce2a805b02ec903c8dd93e25836224e2fc098f19e6ab011a8f2341b299f`

## Objective

Ask one disposable, local, network-isolated PostgreSQL 16 server whether the
accepted inert SQL artifact is server-admissible and whether its resulting
system catalogues match the accepted render manifest. The rehearsal creates
only repository-authored synthetic prerequisite table shapes and the accepted
durability definitions inside a uniquely owned throwaway container. It reads
catalogue metadata, records value-free evidence, and removes the exact owned
container.

The intended result is
`raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`.

This is not an application database, migration, backend, source adapter,
watcher, listener or behavior test. No entry function, trigger function,
trigger, RLS policy or application command is invoked for behavior.

## API Spine classification

This remains internal async durability evidence. GraphQL stays read-only and
unchanged. REST/OpenAPI remains the only command plane and gains no operation.
No application or Diary route is mounted. The accepted update-confirm command
remains the sole future producer boundary, but it is not called or wired here.
Catalogue objects, rehearsal logs and evidence are not truth, command evidence
or authority.

## Exact authority and inputs

The harness accepts no caller-selected image, executable, SQL, contract,
container name, database name, query, output path or cleanup target. It reads
only fixed repository paths for:

1. the exact parent `.sql.inert` bytes and render manifest;
2. one new closed rehearsal contract and its whole-document JSON Schema;
3. one new fixed authored-synthetic prerequisite contract derived from the
   accepted four `public.*` relation signatures; and
4. its own fixed catalogue-query and evidence-schema definitions.

Before daemon contact it verifies the accepted parent source binding, planning
baseline, canonical artifact hash, canonical UTF-8/LF byte count `1405495`,
statement count `412`, PostgreSQL major `16`, six ordered phases and exact
accepted catalogue assertions. The checked-out file may contain Git-managed
CRLF line endings on Windows; the harness permits only mechanical CRLF-to-LF
normalization, rejects lone carriage returns or every other byte difference,
and requires the resulting bytes to equal the manifest hash before use. It
refuses all other parent or contract drift.

The sole executable is the locally resolved `docker.exe`. The harness permits
no executable override and invokes it only as an argument vector with
`shell=False`. A missing Docker client, unavailable daemon or absent exact
image is a contained `environment_unavailable` result, never permission to
download, install, start Docker Desktop, use another runtime or contact a
registry.

## Exact disposable PostgreSQL boundary

The closed runtime profile is:

- exact locally present image reference `postgres:16-bookworm`;
- `--pull=never`, so a missing image fails without registry contact;
- `--network=none`, no published or exposed host port and no network join;
- no bind mount, named volume, workspace mount or Docker socket mount;
- PostgreSQL data on one container-local tmpfs; no durable database bytes;
- a unique closed-prefix container name and two ownership labels containing a
  harness identifier and cryptographically random per-run cleanup nonce;
- one authored-synthetic database/user/password configuration used only to
  satisfy official image initialization; no operational credential and no
  `POSTGRES_HOST_AUTH_METHOD=trust`;
- all `psql` connections executed inside the owned container over its local
  Unix-domain socket; and
- bounded CPU, memory, process, startup, command and total-run time ceilings.

The harness may inspect only the exact image reference, the exact closed
container name, and the exact captured container ID. It must not list global
containers, images, volumes or networks; prune; pull; build; login; start a
desktop application; or delete any object it did not create and reverify.

## Synthetic prerequisite contract

The accepted artifact references but does not create four existing
application relations. The rehearsal therefore creates only these empty
authored-synthetic shapes in `public`, with exact accepted PostgreSQL types and
the minimum named primary/unique constraints required for dependency
resolution:

- `public.appointments`;
- `public.appointment_command_idempotency`;
- `public.appointment_audit_log`; and
- `public.diary_committed_events`.

The contract position-closes every column, type, nullability, default and
synthetic key. `xmin` is never created because it is PostgreSQL's system
column. There are no rows, patient identifiers, product values, triggers,
policies, grants or application behavior in the prerequisites. Their owners
are captured before the accepted artifact is applied and must remain unchanged
afterwards.

The harness creates two fixed empty synthetic databases inside the one owned
cluster: a rollback database and a success database. Because PostgreSQL roles
are cluster-scoped rather than database-scoped, the rollback case must run
first while the accepted roles are absent. It installs the four prerequisite
shapes in the rollback database, streams the fixed invalid canonical copy,
then proves both database-local fabric absence and cluster-wide accepted-role
absence. Only after that proof may it install prerequisites in the success
database and admit the canonical artifact.

Each prerequisite set is installed in one explicit transaction. Each artifact
stream is passed as manifest-bound canonical UTF-8/LF bytes on standard input
to in-container `psql` with `--file=-`, `ON_ERROR_STOP=1` and
`--single-transaction`. `--file=-` is mandatory because psql's single-
transaction mode applies only with `-c`/`-f`; plain implicit stdin is forbidden.
The artifact has already proved that it contains no transaction control; a
failure must roll back its entire fabric-definition transaction. No
`.sql.inert` file is renamed, copied into a migration directory or mounted
into the container.

## Catalogue readback

After the rollback case passes and the canonical artifact succeeds in the
success database, the harness issues only a fixed read-only
catalogue script using `pg_catalog`-qualified relations and functions. The
script emits canonical JSON/TSV facts for exact comparison with the accepted
manifest and closed rehearsal contract. It verifies at least:

- server major version `16`, database identity and empty application tables;
- one `emr4_context_fabric` schema and its exact owner;
- exact four domains, nineteen enums, nine composites and the total
  thirty-two owned fabric types/domains;
- exact eighteen fabric relations, their columns, defaults, constraints,
  indexes, forced-RLS flags and owners;
- exact forty-four policies with roles, command, permissiveness, qualification
  and check expressions;
- exact eight roles and their login/inheritance/bypass/replication ceilings;
- one support function, nine entry functions and fourteen trigger functions,
  including identities, owners, languages, security mode, volatility,
  strictness, parallel safety and fixed search paths;
- exact fourteen trigger declarations, split into seven ordinary immediate
  triggers and seven constraint/deferred triggers, with exact target relation,
  timing, level, event mask, function, enablement and deferrability;
- exact schema/table/function revocations and grants, including no runtime
  schema `CREATE`, no runtime trigger-function `EXECUTE`, and no broader
  `PUBLIC` authority; and
- zero application-relation owner changes, zero application rows, zero
  extension additions and no unexpected object in the fabric schema.

All returned facts are allowlisted metadata. Raw server logs and SQL error text
are retained only in bounded redacted form: SQLSTATE, stage, exit code and a
fixed-length digest. No catalogue value can select a later command or cleanup
target.

## Negative and rollback evidence

Repository tests challenge the harness without requiring Docker. They prove
that it rejects parent/hash/image/path/query drift, shell use, pull/build/login,
network or port options, mounts/volumes, caller arguments, broad Docker
enumeration, trust authentication, non-owned cleanup and incomplete catalogue
claims.

Before successful admission, the disposable server run performs a mutation
copy in memory: one fixed synthetic invalid top-level statement is appended
after the accepted bytes and streamed through `--file=-` and the same single-
transaction admission path into the rollback database. The expected syntax
SQLSTATE is recorded. Database-local catalogue readback must show no
`emr4_context_fabric` schema or object, and cluster-wide role readback must show
no accepted role. Only then may the success database receive the canonical
artifact. The canonical artifact is never modified.

This negative case proves transaction rollback for installation failure only.
It does not execute any function or trigger behavior.

## Cleanup and proof of absence

Cleanup runs from `finally` after any post-create outcome. Before removal the
harness inspects the exact captured container ID and requires all of:

1. exact ID equality;
2. exact closed container name;
3. both exact ownership labels and nonce;
4. `NetworkMode=none`;
5. no bind or volume mount; and
6. the expected image identity.

If ownership cannot be reverified, the harness refuses destructive cleanup and
returns `cleanup_ownership_unverified` with the exact container ID for human
inspection. It must not substitute a name, prefix, list or label query. When
ownership is verified it force-removes only that exact ID, then an exact-ID
inspect must return the documented absent condition. No image, volume, network,
database outside the container, workspace file or unrelated container is
removed.

## Allowed artifacts

This tranche may add only:

- this plan, one design and one threat-model delta;
- one closed rehearsal contract, prerequisite contract and their JSON Schemas
  under
  `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/`;
- one standard-library-only fixed-path harness;
- one provider-free disposable-run evidence JSON;
- authored-synthetic static, hostile and exact evidence tests;
- bounded review packets and receipts; and
- closeout, acceptance, error-register and Continuity/Compass artifacts.

No further parent artifact, Alembic file, application source, API, Diary code,
runtime configuration or dependency declaration may change. The exact
composite-ordering parent correction and its immutable failed evidence are
position-closed in
`docs/raisa-provider-free-unmounted-durability-inert-ddl-composite-dependency-ordering-recovery.md`.

## Acceptance

Acceptance requires all of the following:

1. the accepted parent HEAD, planning baseline, canonical UTF-8/LF artifact
   hash and byte count, statement count, major version and render-manifest
   assertions are exact and parents remain unchanged;
2. the rehearsal and prerequisite contracts are whole-document schema-valid,
   fixed-path, position-closed and admit no caller/environment-selected input;
3. Docker invocations are argv-only and contain exact no-pull, no-network,
   no-port, no-mount, no-volume and resource/time boundaries;
4. preflight proves the exact image is already local without pulling, and a
   missing client/daemon/image terminates without fallback;
5. the captured container configuration and ownership labels match the closed
   profile before any SQL is sent;
6. prerequisite DDL creates exactly four empty synthetic application shapes
   and never creates `xmin` or application behavior;
7. PostgreSQL 16 first rejects the fixed invalid copy through
   `--file=-`, `ON_ERROR_STOP=1` and `--single-transaction`, leaving no
   database-local fabric object or cluster-wide accepted role, and only then
   admits the exact parent bytes through the same atomic file-input mode;
8. canonical catalogue readback matches every closed type, object, relation,
   policy, role, function, trigger, owner, privilege and search-path assertion;
9. application relation owners and empty row counts remain unchanged;
10. the fixed invalid-copy case runs before success and leaves no fabric schema
    in its rollback database and no accepted role anywhere in the disposable
    cluster;
11. no entry function, trigger function, trigger, policy or application
    command is behaviorally invoked;
12. evidence records exact parent/run/image/config/catalogue/rollback/cleanup
    facts without patient, product, credential or unrestricted log content;
13. exact owned-container cleanup succeeds and exact-ID post-inspect proves
    absence, or the tranche fails closed without touching an unverified target;
14. static hostile tests, focused tests, Ruff, deterministic evidence
    verification and explicit Git pre/postflight pass; and
15. one fresh exact-HEAD independent architecture veto reports no material
    finding and leaves its bounded review worktree unchanged.

## Data, provider, cost and licence posture

- Runtime data: repository-authored metadata and empty authored-synthetic
  relation shapes only.
- Patient, product, protected and historical-PHI data: none.
- Database: one local disposable PostgreSQL 16 container only after plan
  acceptance; no operational source or database.
- Network: Docker container network is `none`; image pulling and all registry,
  provider, browser and product traffic are forbidden.
- Model review: the already allocated development verifier may receive only
  the fixed repository-local plan/code/evidence packet; no provider product
  route or data is opened.
- Cost: zero cloud/product/database cost; no paid runtime call.
- Licence: accepted repository content and the locally present official
  PostgreSQL image only; no external corpus or new dependency.

## Worker allocation

Sol owns planning, implementation, the serial disposable runtime, recovery,
acceptance and cleanup because container ownership and evidence are tightly
stateful. A fresh Gemini 3.6 Flash/high Antigravity context may perform the
read-only exact-HEAD architecture veto over the bounded packet. No worker may
start a container, accept its own work, write the primary worktree, push, move
a protected ref or broaden the gate.

## Recovery and stop

A syntax, dependency, catalogue or harness defect receives evidence-backed
diagnosis and bounded repair within this exact descendant, followed by a fresh
run in a newly owned container and a fresh veto. A missing local image or
Docker daemon is an environment stop, not authority to install, pull, log in or
use another database. Cleanup ownership uncertainty stops destructive action.

Pause for Yuri only if recovery exposes a genuinely non-inferable product,
privacy, security, licence or operational decision outside this plan, or a
human-only environment action is required. Routine plan repair, test failure,
PostgreSQL rejection, catalogue mismatch or reviewer correction is not a user
gate.

At tranche close Sol gives a lay summary of capability gained, surfaces kept
closed and issues found/resolved, then immediately enters the next
dependency-satisfied planned gate unless Yuri's intervention is genuinely
necessary.

## Claim boundary and next dependency

Passing proves only that PostgreSQL 16 accepted this exact authored-synthetic
installation transaction, produced the expected catalogue shape and privileges,
rolled back one fixed failed installation, and was removed under verified
ownership. PostgreSQL function creation does not prove every embedded SQL
branch resolves or behaves correctly at execution time.

It does not prove entry/trigger behavior, RLS enforcement, concurrency,
idempotency, rollback of application work, unknown-commit recovery, migration
upgrade/downgrade safety, application-schema compatibility beyond the four
synthetic shapes, performance, runtime wiring, source observation, patient or
product safety, deployment or production readiness.

Only after this tranche passes may a separately planned provider-free
database-backed authored-synthetic behavior/transaction rehearsal be
considered. Alembic integration, application runtime wiring, operational
credentials, live source/product data, providers, deployment, production,
release, Pages and protected-ref movement remain closed.
