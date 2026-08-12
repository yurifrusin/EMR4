# Status-confirm physical schema-and-transaction scaffold

Date: 2026-08-12

Result: `raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold_pass`

Source: `b36b8a455b70d8bc3e99b5e5dd84a8237375ff3c`

## Lay summary

The safer appointment-status design now exists as code, but it is still
disconnected from the live application.

Appointments have a mapped database revision number, and private retry receipts
have places for the before/after versions, an opaque session fingerprint and the
exact response bytes. The proposed database upgrade advances revisions itself,
so an application caller cannot quietly choose or suppress the number. The new
helper also lines competing work up in the agreed practice → appointment → retry
record order and checks current authority before revealing retry information.

Crucially, none of this has been installed or wired into a button or route. The
helper refuses to commit a new command unless a later, separately approved
kernel supplies the full appointment change, audit and receipt together.

## Technical summary

The source adds a positive non-null `BIGINT` appointment version, five private
nullable receipt columns, a seven-phase inert Alembic migration with a
PostgreSQL-owned `BEFORE UPDATE` trigger, fixed-order canonical UTF-8 bytes,
domain-separated length-framed HMAC-SHA-256 session binding and constant-time
digest validation. The unmounted seam uses one bounded `READ COMMITTED`
transaction and conflict-safe insert/lock handling with two authority checks.

All 16 bindings, 80 hostile mutations, 11 focused tests and 274 current
descendant tests pass. The public OpenAPI contract is unchanged.

## Deliberately closed

No migration or SQL was executed; no database, real lock or route was opened;
no patient/product data, provider/ADC, credential or browser authorization,
watcher/event, command, deployment, production, release, Pages or protected ref
was used or moved.

## Next work

The next tranche is a disposable PostgreSQL parse/catalogue rehearsal. It will
test whether this exact inert migration installs into an owned empty database
and produces the intended columns, constraints, function and trigger, while
rolling back authored-synthetic probes and cleaning up completely.

Yuri attention required: `no`.
