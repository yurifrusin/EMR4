# Provider-free durability interval-construction recovery

Date: 2026-08-09

Status: bounded renderer and authored-synthetic harness recovery candidate;
behavior runtime remains closed

## Preserved failure

Behavior attempt 024 passed generation registration and reached `BTR-E02`,
then failed closed with SQLSTATE `42883`. It admitted zero complete scenarios
and removed exact owned container
`61a367f04b85b89b35af3abd5fb5390e94a0a44a7d290022554f443ea8c5f86a`;
exact-ID absence was verified. Its immutable evidence is
`provider-free-behavior-transaction-failure-evidence-024.json`, byte-identical
to the failed mutable artifact at SHA-256
`sha256:bc2efc6fffea47e8104324c822bd6c1afde28f746b05b2a5bff925dbbfe7f57b`.

The first diagnostic parser failed locally without releasing raw database text
or a conclusion and is preserved as AER-0158. A separate corrected diagnosis
then replayed the exact closed BTR-E01/E02 path and ran a fixed read-only
catalogue-resolution probe immediately before BTR-E02. Five of six candidate
symbols resolved; the sole missing signature was
`pg_catalog.*(integer, interval)`. Raw PostgreSQL output was hashed but not
persisted, and the newly owned diagnostic container was removed with absence
verified.

## Root cause

Two repository-authored SQL generators used the same invalid expression shape:

- typed `TIMESTAMP_ADD_MINUTES` and `TIMESTAMP_ADD_SECONDS` lowering emitted a
  numeric value on the left of `*` and an interval on the right; and
- the closed BTR-E02 authored-synthetic event-payload fixture independently
  emitted the same integer-times-interval shape.

PostgreSQL 16 does not expose the diagnosed `integer * interval` operator.
PostgreSQL documents `make_interval` as the typed constructor whose `mins`
argument is integer and whose `secs` argument is double precision, and
documents `timestamptz + interval` as the intended timestamp addition form:
<https://www.postgresql.org/docs/16/functions-datetime.html>.

The parse/catalogue rehearsal did not reveal this defect because PostgreSQL can
store PL/pgSQL function bodies without executing every embedded expression.
Attempt 024 was the first accepted path to execute BTR-E02.

## Exact recovery

Renderer 2.0.11 must:

1. lower minute offsets as
   `timestamp + pg_catalog.make_interval(mins => integer_expression)`;
2. lower second offsets as
   `timestamp + pg_catalog.make_interval(secs =>
   (integer_expression)::pg_catalog.float8)`;
3. reject every remaining numeric-times-`make_interval` spelling in the
   independent recognizer; and
4. leave the immutable typed body contract, structural contract, entry points,
   triggers, roles, policies and effects unchanged.

The deterministic regenerated result is exactly 412 statements and 1,391,614
canonical LF bytes at SHA-256
`sha256:c113b2480106441043562412ee3135d2a79bd56c76bb5bc2705734d9e5f8cf51`;
its render-manifest file SHA-256 is
`sha256:7a0c5d15e65a4631cf9b590f7c7af67f2103f69ebe05fb2dd9ad5f002e1d1b2d`.
The exact artifact path is also forced to `eol=lf` in `.gitattributes`, so a
fresh Windows review worktree cannot silently change its canonical bytes.

The behavior fixture must independently construct its exact synthetic end time
with `make_interval(mins => fixed_duration)`. No scenario coordinate, SQLSTATE,
principal, isolation rule, expected effect, rollback rule or readback is
changed.

## Required proof sequence

Before another behavior run:

1. focused renderer, recognizer, fixture, diagnosis and immutable-failure tests
   pass;
2. the inert 412-statement artifact and manifest are regenerated from the
   unchanged structural/body parents;
3. one newly owned networkless PostgreSQL 16 characterization container proves
   the resulting catalogue digests and is removed;
4. only then is the exact catalogue contract rebound and reproduced in a
   separate newly owned exact-bound container;
5. the behavior contract is rebound to the accepted parse source with its
   twenty ordered scenarios and `6/4/3/4/3` population unchanged;
6. the complete deterministic/hostile packet and one fresh exact-HEAD Gemini
   3.6 Flash/high veto pass; and
7. one newly owned networkless behavior container runs the next attempt with
   exact-ID cleanup.

Any new failure continues the same evidence-backed diagnose-repair-rerun
sequence. It never authorizes scenario removal, superuser substitution,
untyped raw SQL, RLS/trigger disablement or operational runtime.

## Claim and authority boundary

This recovery proves only valid typed interval construction in the inert
artifact and closed authored-synthetic rehearsal payload. It grants no applied
migration, operational database, product or patient data, provider, application
or API/Diary wiring, watcher/listener/feed, command/write, deployment,
production, release, Pages or protected-ref authority.
