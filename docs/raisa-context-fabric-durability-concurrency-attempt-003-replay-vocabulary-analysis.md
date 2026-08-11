# Context Fabric durability concurrency attempt 003 replay-vocabulary analysis

Date: 2026-08-11

## Result

Attempt 003 is rejected and consumed. It failed closed at the fresh replay after
`CFD1-C05`; the exact disposable PostgreSQL container was removed and its
absence was verified. The attempt made zero provider calls, product reads,
product commands or external-network operations.

The marker telemetry recovery worked as designed. The immutable failure
evidence identifies `c05_exact_coordinator_replay`, principal
`context_coordinator`, `serializable` isolation, expected closed marker
`RECEIPT_REPLAY`, zero admitted observed markers, ten started participant
transactions and ten started precondition transactions.

## Diagnosis

The failure is a deterministic CF-D1 harness vocabulary defect, not a database
or accepted durability-contract failure.

- The accepted inert PostgreSQL enum
  `emr4_context_fabric.durability_transition_result_kind` contains
  `RECEIPT_REPLAYED`.
- The accepted transition function returns `RECEIPT_REPLAYED` for the exact
  stored-receipt replay branch.
- The previously accepted serial behavior harness expects
  `RECEIPT_REPLAYED` for `BTR-I03`.
- CF-D1 alone allowlisted and expected the misspelling `RECEIPT_REPLAY`.

The fresh replay therefore succeeded at PostgreSQL but its valid scalar was
excluded by CF-D1's closed result parser. The parser released an empty observed
marker list and failed closed exactly as required.

## Bounded correction

Replace only the CF-D1 misspelling with the accepted native enum value
`RECEIPT_REPLAYED` in the result vocabulary, both coordinator replay
expectations and the evidence schema. Add a regression test that binds the
closed parser, schema and both replay coordinates to that exact native value
and rejects the misspelling.

The accepted inert SQL, fixture facts, race topology, transaction isolation,
wait-event proof, readback assertions, parent evidence and runtime authority do
not change. Attempt 003 remains immutable. A distinct attempt 004 is ineligible
until the correction passes deterministic tests and a fresh clean exact-HEAD
Gemini 3.6 Flash/high review.

## Boundaries

This recovery authorises no provider call, patient or product data, operational
database, source or watcher access, executable product tool, product command,
deployment, production, release, Pages rebuild or protected-ref movement.
