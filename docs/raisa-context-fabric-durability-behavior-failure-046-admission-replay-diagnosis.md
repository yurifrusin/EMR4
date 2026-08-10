# Context Fabric behavior failure 046: admission replay diagnosis

Date: 2026-08-08

Status: immutable bounded failure diagnosed; no rerun

Attempt 046 (`e4db8cf23eb421e40744ea25`) reached the third transaction
of `BTR-I02` and stopped in
`emr4_context_fabric.admit_proofread_observation_v1` with SQLSTATE `CF004`.
The run released no scenario pass, removed its exact owned container and
independently confirmed that container's absence. Its immutable evidence has
SHA-256 `ea2fc7f55121604b8f68b5bbacc55b97c98ead76a5793b6d7c766f2269b311c0`.

Repository-only diagnosis identifies one exact contradiction. Each of the
three `INSERT_OR_RELOAD_COMPARE` admission nodes correctly writes the
server-authored `admitted_at` value with `transaction_timestamp()`, but also
requires a pre-existing winner's `admitted_at` to equal the replay
transaction's new timestamp. On the repeated conflict call, the primary key
correctly suppresses a duplicate insert; the reload comparison then cannot
recognise the already committed winner and translates the empty strict reload
to `F_CARDINALITY` / `CF004`.

The bounded recovery removes only the `admitted_at =
transaction_timestamp()` term from the three winner predicates. It preserves:

- the exact eight-column conflict key and primary-key enforcement;
- database-authored `admitted_at` insertion, storage and returned row image;
- every other winner comparison;
- all roles, capabilities, RLS, SQLSTATE, transaction and command boundaries;
- the immutable body and structural parent contracts.

No additional container, provider/model call, operational database,
watcher/feed, application/API/Diary wiring, patient/clinical/product data,
deployment, release, Pages or protected-ref movement was opened by the
diagnosis. A fresh rendered candidate, parse/catalogue admission and independent
veto are required before any new behavior attempt.
