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
execution deadline reserves bounded time for exact-ID cleanup.

The expected PostgreSQL-16 deparse digests cannot safely be guessed from the
source spelling. The repaired contract therefore begins in
`characterization_only`: one fresh-vetoed, exact-artifact disposable run may
record only bounded canonical query digests, can never emit the pass result,
and must still prove rollback and exact cleanup. Those digests may then be
position-closed into `exact_digest_bound`, with the whole contract hash updated
and a fresh exact-HEAD veto before the terminal rerun. This is a bootstrap of
expected metadata, not acceptance by observation; the terminal run remains a
separate newly owned container and must match every frozen digest.

## Claim boundary

This recovery grants no database execution until the repaired characterization
candidate receives a fresh replacement veto,
and no application behavior, RLS/trigger execution, Alembic integration,
operational persistence/credential/source, patient/product data, API/Diary,
provider product path, deployment, production, release, Pages or protected-ref
authority.
