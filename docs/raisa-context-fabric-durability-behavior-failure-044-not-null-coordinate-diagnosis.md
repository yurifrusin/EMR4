# Context Fabric durability behavior failure 044 — not-null coordinate diagnosis

Date: 2026-08-08

Immutable attempt 044 reached `BTR-I02` and safely rejected with PostgreSQL
SQLSTATE `23502`. Cleanup and exact container absence passed. The protected
mutable evidence alias was restored byte-exactly, and attempt 044 will not be
rerun.

The evidence identifies the scenario and SQLSTATE but not the affected relation
or column. This is a harness telemetry gap, not evidence yet of which database
expression is wrong. The harness already has a bounded PostgreSQL not-null
header/diagnostic parser for bootstrap failures; the success-scenario rejection
path did not use it.

The narrow correction reuses that parser with an exact allowlist limited to the
twenty typed columns of
`emr4_context_fabric.context_proofread_observation_admission`. Only SQLSTATE,
coordinate status and an allowlisted relation/column may be released. Unknown
relations or columns remain hidden and raw stderr remains digest-only. The
database body, DDL, behavior contract, fixtures and scenario order do not
change.
