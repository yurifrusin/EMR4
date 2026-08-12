# Status-confirm physical-design architecture

Date: 2026-08-12

Result: `raisa_provider_free_unmounted_status_confirm_physical_design_architecture_pass`

Source: `826aad11c29007b13eaa377e3f7ea494cc82ce70`

## Lay summary

We have now chosen how the safer status change will fit into the database,
without installing it yet.

Each appointment will carry a database-owned revision number. Every committed
change moves it forward, so an old confirmation can be recognized honestly as
old. A successful command will also leave one private receipt containing the
before/after revisions and the exact response bytes originally returned. A
retry can therefore receive the same answer, not a reconstruction that merely
looks similar.

Competing commands line up in one order: practice, appointment, then retry
record. The winner commits the appointment, audit and receipt together. A
loser gets a safe explicit outcome; revoked users and corrupt or old-format
receipts reveal no stored result.

## Technical summary

The accepted architecture selects PostgreSQL `BIGINT` revision ownership via a
synchronous `BEFORE UPDATE` invariant; a seven-phase cutover with baseline-one
backfill; five additive, nullable-for-legacy receipt columns; 32-byte
domain-separated HMAC session binding; canonical UTF-8 JSON byte storage; and a
bounded `READ COMMITTED` `FOR SHARE`/`FOR UPDATE`/`FOR UPDATE` lock sequence.

The public OpenAPI envelope is unchanged. Legacy rows remain unversioned and
non-replayable under the new contract. All 11 hashes, 91 hostile mutations, 16
focused tests and 413 combined tests pass. Two early test failures were only
line-wrap assertions and did not alter the design.

## Deliberately closed

Nothing is mounted or run. There is no executable migration, ORM/service/route
implementation, database execution, real lock, provider/ADC use, credential
action, product/patient data, watcher/event authority, product command,
deployment, production, release, Pages or protected-ref movement.

## Place in Raisa and next work

This is the physical bridge from the source-owned-truth safety kernel to future
runtime code. The next tranche will implement only an unmounted scaffold of the
exact schema and transaction contract, with static deterministic proof before
any database or route is exercised.

Yuri attention required: `no`.
