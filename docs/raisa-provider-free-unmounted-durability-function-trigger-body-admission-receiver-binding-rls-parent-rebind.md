# Durability function/trigger body admission-receiver binding-RLS parent rebind

Date: 2026-08-10

Status: deterministic parent rebind; body programs unchanged

The function/trigger body contract now binds structural parent
`sha256:ff64b568d65d243ad5bb3dd8159063f47732b0b360efcc12f58d3b28ceb00d9a`.
The only parent delta is `pol_cf_17_select`: the forced-RLS binding read now
recognizes exactly the existing `context_schema_owner` and
`context_admission_receiver` as function owners while retaining the exact
authenticated `session_user` and active-time row fences.

All typed body programs, declarations, operands, predicates, failure
identities, lock nodes, effects, call graph, role grants and renderer order are
unchanged. In particular, `admit_proofread_observation_v1.binding.select`
remains the same `SELECT_EXACT` session-bound read, and the receiver retains
only its previously accepted exact binding-table `SELECT` and admission-row
`INSERT`.

This rebind grants no third owner, runtime login, role membership, RLS bypass,
new table privilege, body-program change, applied migration, database,
product/patient, provider, command, deployment, release, Pages or protected-
ref authority.
