# Disposable PostgreSQL parse/catalogue plan recovery

Date: 2026-08-07

Status: mechanics and population corrections accepted; exact-definition
implementation recovery is in progress before any Docker or PostgreSQL action

## Rejected review

The first exact-HEAD Gemini 3.6 Flash/high plan review returned `pass` at
`d202b310318496fb7a414d97916bbac54e6ec349`. Sol did not admit it. The review
missed two material PostgreSQL mechanics even though its packet explicitly
challenged atomic admission and rollback.

First, PostgreSQL roles are cluster-wide. The candidate scheduled a successful
installation before a failed-copy rehearsal in a second database within the
same cluster, then expected no accepted role to survive the failure. Roles from
the earlier success would already exist cluster-wide, and the later artifact's
`CREATE ROLE` statements would collide before testing the intended late
rollback.

Second, PostgreSQL 16 documents that psql `--single-transaction` can be used
only with one or more `-c`/`-f` options. The candidate streamed bytes over plain
implicit stdin, so its atomicity claim did not bind the CLI mechanism that
actually supplies the outer transaction.

No Docker or PostgreSQL action had occurred. The review receipt remains
preserved but has no acceptance authority.

## Exact recovery

The corrected lifecycle remains one owned, networkless, disposable PostgreSQL
16 container but creates two fixed empty synthetic databases. It runs the
invalid-copy transaction first while accepted roles are absent, proves no
fabric object in the rollback database and no accepted role in the cluster,
then admits the canonical bytes into the success database and performs exact
catalogue readback.

Both artifact streams use exact `psql --file=- --single-transaction` argv with
`ON_ERROR_STOP=1`; standard input supplies the file named `-`. Plain implicit
stdin is forbidden. Every prior no-pull, no-network, no-port, no-mount,
synthetic-only, exact-ownership and cleanup boundary remains unchanged.

The corrected plan requires deterministic recovery checks and a genuinely
fresh exact-HEAD independent veto before any Docker or SQL action.

## Exact-catalogue population correction

Sol's final manifest reconciliation after the replacement review found that
the total owned type/domain population `32` was correct but the plan's split
was transposed. The accepted render manifest contains exactly four `DOMAIN`,
nineteen `ENUM` and nine `COMPOSITE` nodes, not four/seventeen/eleven. The
replacement reviewer reported only the correct total and did not challenge the
incorrect subdivision despite its catalogue-completeness assignment.

The plan and design now bind exact `4/19/9/32`. No runtime action had occurred.
A fresh exact-HEAD veto at `c5f0960a240b7f162b1b34e1b09fb166d12fd42e`
mechanically reproduced all 388 ordered nodes, every exact type identifier and
the 4/19/9/32 population, passed 9/9 focused checks and left its worktree clean.
Sol independently reproduced the same counts and one-to-one type-owner set.

## Exact-definition implementation correction

The first implementation veto returned `pass` at
`1fd3445aea5839b7aa889fc962faa8ad2be0c95e`, but Sol did not admit it. The
harness compared exact object populations while accepting arbitrary same-name
column/default, constraint/index, policy-expression, function-attribute,
trigger-definition and non-owner ACL details. The review described these
surfaces as exact without mechanically mutating them. Sol found the gap before
Docker resolution, daemon contact or SQL execution.

Recovery expands the fixed PostgreSQL catalogue projections so their digests
cover domain definitions, enum labels, composite attributes, every fabric and
prerequisite column, constraint/index definitions, policy roles and
expressions, function identities/results/attributes/search paths, trigger
timing/level/event masks/deferrability and every explicit non-owner
schema/relation/function privilege. Resource readback now includes exact
memory, CPU, PID, tmpfs, port and synthetic environment facts, and an absolute
execution deadline reserves bounded time for exact-ID cleanup. A subsequent
Sol post-veto check also found that output was rejected only after
`communicate()` had accumulated it; the repaired runner now drains stdout and
stderr concurrently into hard byte-capped buffers and terminates the child at
the cap, so rejection is a real memory boundary rather than a retrospective
size check.

The first image-restored characterization attempt then stopped before container
creation because Docker Desktop reports an absent container as `No such
container`, while the exact-absence recognizer admitted only `No such object`.
The failed evidence is preserved. Recovery accepts only those two documented
nonzero exact-inspect absence phrases; success, daemon failure and every other
response remain non-absence and cannot authorize creation or cleanup.

The next newly owned attempt reached exact-ID containment verification and
failed closed before readiness or SQL because Docker Desktop position-closes a
`--tmpfs` declaration in `HostConfig.Tmpfs` while leaving its normalized
`Mounts` projection empty. Exact manual inspection reproduced every ownership
label, nonce, ID, name, image, network, resource, port, restart and tmpfs
`HostConfig` fact; Sol then removed only that exact verified ID and exact-ID
inspection proved absence. The failed evidence and manual-cleanup receipt are
preserved. Recovery continues to require the exact `HostConfig.Tmpfs` path and
options and rejects every other mount, but accepts either Docker Engine's one
matching normalized tmpfs row or Docker Desktop's empty normalized projection.

The following newly owned attempt passed containment, readiness, rollback-
database creation and authored-synthetic prerequisite installation, then the
canonical parent bytes failed before the fixed invalid suffix. Exact source
inspection found the deterministic dependency defect: the emitted
`generation_registration_v1` composite referenced `future_key_interval_v1`
before that referenced composite was created. Automatic exact-ID cleanup
passed. The attempt remains preserved as non-acceptance evidence.

This finding narrowly reopens the otherwise immutable parent-artifact boundary
for one renderer-derived correction: composite definitions are emitted in a
stable dependency-safe topological order, preserving source order whenever it
is already legal and failing closed on duplicate names or cycles. No composite
name, field, type, owner, object population, statement population, function,
trigger, policy, privilege or application relation may change. The canonical
artifact and manifest must be regenerated by the fixed parent compiler, then a
descendant disposable contract must bind the corrected source HEAD, artifact
hash and byte count. Static regeneration, hostile ordering tests and a fresh
exact-HEAD veto precede any further Docker or PostgreSQL action.

The corrected compiler/artifact source is
`4911cba926cb69b4f7f945a77d744ff07ab2d3d4`. It preserves 412 statements and
1,405,495 canonical LF bytes while changing the artifact SHA-256 to
`5e23fce2a805b02ec903c8dd93e25836224e2fc098f19e6ab011a8f2341b299f`.
The descendant rehearsal contract binds that exact source and artifact; it
remains in non-passing `characterization_only` mode pending fresh veto.

The first corrected-artifact attempt then passed exact container ownership and
a single `pg_isready` result but failed the immediately following first
database-create command. It completed automatic exact-ID cleanup. This is the
official image's bounded bootstrap-to-final-server handoff window: a socket
handshake alone does not prove a stable authenticated SQL endpoint. Recovery
therefore requires the fixed `pg_isready` probe and a fixed authenticated,
read-only server-major SQL probe to succeed continuously for three seconds;
any failure resets the stable interval. The probes expose no application row,
invoke no fabric function and remain inside the existing 45-second startup and
300-second total deadlines.

The expected PostgreSQL-16 deparse digests cannot safely be guessed from the
source spelling. The repaired contract therefore begins in
`characterization_only`: one fresh-vetoed, exact-artifact disposable run may
record only bounded canonical query digests, can never emit the pass result,
and must still prove rollback and exact cleanup. Those digests may then be
position-closed into `exact_digest_bound`, with the whole contract hash updated
and a fresh exact-HEAD veto before the terminal rerun. This is a bootstrap of
expected metadata, not acceptance by observation; the terminal run remains a
separate newly owned container and must match every frozen digest.

The first readiness-stability attempt `e2654735548d0ba3588ef372` then remained
inside readiness until its 45-second startup budget was exhausted. It performed
no database create, rollback or catalogue action, and exact-ID cleanup removed
container `1abe609a746022bd2855f78e1677d2c7e3bdf428dc861bc0c86bfc4b1c196d8f`
and proved absence. The failure record could identify only a generic process
timeout, so it could not distinguish a socket rejection from an authenticated
probe handoff. Recovery gives only the fixed read-only readiness `psql` command
a bounded `PGCONNECT_TIMEOUT`, removes its unused interactive-stdin flag,
translates host probe timeout into an exact readiness operation, and records
only bounded counts, exit codes and output digests. It adds no write retry and
does not retain raw logs or values.

Attempt `8e60fe0d1df3ec3aec09b364` then proved the connection-timeout hypothesis
wrong: 82 of 83 `pg_isready` calls succeeded, while all 82 authenticated SQL
probes returned exit 1 with one stable stderr digest and no stdout. No database
create, prerequisite, artifact or catalogue step began, and exact-ID cleanup
removed `8194e86caee7d2db2380e44761dcfc50ad861fc7ff0b67b0a323e6912d38836f`
and proved absence. PostgreSQL 16 documents that a connect timeout of one is
interpreted as its minimum two seconds, so the contract and prose now state two
seconds. The server-major query now returns the documented six-digit
`server_version_num` text directly and validates it locally as PostgreSQL 16,
removing unnecessary SQL casts. A fixed value-free classifier records only a
closed diagnostic category if any SQL probe still fails; raw stderr remains
digest-only.

The direct-query attempt `ea70edf697e7afc979f01d9a` then passed stable
authenticated readiness, created the rollback database and installed all four
empty prerequisite relations. The streamed invalid installation returned the
expected psql exit 3 but did not expose expected SQLSTATE `42601` to the old
checker, so the run stopped before rollback absence readback or the success
database. Exact-ID cleanup removed
`4d9f9a40341b6f9e117f4c50c2f898ac3859f33e044e898e527aa458332e0a4a`
and proved absence. This is consistent with an earlier artifact rejection but
does not establish its error. Recovery now records psql exit, stderr digest,
expected-SQLSTATE presence and only sorted unique five-character SQLSTATE codes
from verbose stderr before failing closed; no raw message or SQL value is
retained.

Attempt `6ea7c4ed9d5c79df86e9f73c` reproduced stable readiness and returned bounded
SQLSTATE `42704`; rollback stderr was exactly 116 bytes with SHA-256
`1bac1a987ff9446ef3724201b06318fb8f9fc16a9aea12df020e16d005e27601`.
A bounded reconstruction of PostgreSQL's verbose error for artifact line 29,
`pg_catalog.smallint` missing at `typenameType` in `parse_type.c:270`, has the
identical byte count and digest. This mechanically identifies the first
failure: the renderer schema-qualified SQL aliases (`smallint`, `integer`,
`bigint`, `boolean`) rather than their physical catalog names (`int2`, `int4`,
`int8`, `bool`). The parent renderer now preserves logical contract type names
but emits only physical names into SQL, including hard-coded xid/count and
boolean literal paths. No application type or semantic digest preimage changes.

## Claim boundary

This recovery grants no further database execution until the corrected parent
artifact, descendant characterization contract and fresh replacement veto all
pass,
and no application behavior, RLS/trigger execution, Alembic integration,
operational persistence/credential/source, patient/product data, API/Diary,
provider product path, deployment, production, release, Pages or protected-ref
authority.

## Descendant binding after physical type recovery

Parent recovery commit `79e490d204e3383ecc14a41c9a5de94429da65f5`
binds the corrected 412-statement artifact at canonical UTF-8/LF SHA-256
`e478cc60a02196bce72e2ea219f792d2f2ba0fe01e076754b0ebbdfd80ef7b18`
and `1404044` bytes. The disposable descendant may admit only those exact bytes.
Its characterization-only result remains incapable of passing, and any fresh
database contact still requires exact-HEAD independent veto and a separately
owned throwaway container.

## PostgreSQL system-column recovery

Attempt `42e97f89776a5652c02b631b` proved the physical catalog-type repair: the
server passed stable authenticated readiness, created the rollback database,
installed all four empty prerequisites and advanced to bounded SQLSTATE
`42701`. It retained only a 136-byte stderr digest and removed exact container
`2e22319964fdd46c1c875d56208283f0766031076925dcb9934d467ee4cdc1fa`,
with absence verified. Catalogue and success-database work did not start.

The first emitted fabric table declared `xmin pg_catalog.xid`. PostgreSQL
defines `xmin` implicitly on every table and prohibits it as a user-defined
column, including when quoted. The immutable model's synthetic `xmin` entry is
still required for typed provenance analysis, but the renderer must omit it
from all eighteen physical `CREATE TABLE` column lists and fail closed if its
accepted modeled shape drifts. This recovery changes no logical relation,
provenance expression, constraint, function, trigger, RLS policy or authority.

Parent recovery commit `b9ffa0cbac24e08d130a8dcb9653678f81fa4268`
binds the resulting 412-statement canonical artifact at `1403432` LF bytes and
SHA-256 `931b0eab6438dfcaf1b1836861972aa25a7f8619e3eaae7edfa3e941cb5f70d2`.
The descendant contract must bind these exact values before any replacement
review or runtime.

## Relation dependency-family recovery

Attempt `375b7a28c8ddf543486145e7` passed stable authenticated readiness,
rollback-database creation and all four empty prerequisites, proving the
system-column correction. The artifact then stopped with bounded SQLSTATE
`42P01`, retained only a 160-byte stderr digest and removed exact container
`57c529683ee441a226b8190ba097ca2b445b0dc9a047807f6d6dc4042102132e`,
with absence verified. Success-database and catalogue work did not start.

The renderer interleaved each table with its constraints, so the first forward
foreign key could name `context_observer_generation` before that relation was
created. The recovery preserves accepted relation order within four physical
statement families: create all tables; establish every primary/unique key;
add every foreign key; then add every check. This handles forward references
and relation cycles without changing any object, field, constraint or policy.
