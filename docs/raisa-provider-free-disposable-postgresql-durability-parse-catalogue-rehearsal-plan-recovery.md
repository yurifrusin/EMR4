# Disposable PostgreSQL parse/catalogue plan recovery

Date: 2026-08-07

Status: accepted after fresh exact-HEAD replacement veto at
`009395ac28eb7ac05017fe5fbd1ae1439ecf948d`

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

## Claim boundary

This recovery grants no database execution until the replacement veto passes,
and no application behavior, RLS/trigger execution, Alembic integration,
operational persistence/credential/source, patient/product data, API/Diary,
provider product path, deployment, production, release, Pages or protected-ref
authority.
