# Provider-free behavior rehearsal snapshot query-id schema recovery

Date: 2026-08-08

Status: deterministic repair candidate; runtime closed pending fresh veto

The attempt-010 regression validated the complete preserved failure envelope
and found that its fixed `query_id` was absent from the closed evidence schema.
This was a contract omission in the diagnostic repair, not a new PostgreSQL
runtime result. Deterministic verification stopped before independent review or
another database rehearsal.

The evidence schema now admits `query_id` only with the constant value
`scenario_snapshot`. A negative test rejects any other identifier. The schema
remains closed to additional properties, stderr prose, query text, query values
and database rows. This change grants no runtime, provider or product-data
authority.
