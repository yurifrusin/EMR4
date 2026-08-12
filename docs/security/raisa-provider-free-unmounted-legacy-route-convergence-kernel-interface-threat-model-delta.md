# Threat-model delta — unmounted legacy-route convergence kernel interface

Date: 2026-08-12

Status: `provider_free_unmounted_design_only`

## Assets

- current appointment and schedule truth;
- staff authority and confirmer attribution;
- conditional precondition integrity;
- one-effect idempotency and original receipts;
- mutation and rejected-attempt audit meaning; and
- the compatibility-to-command migration order.

## New threat cases and controls

| Threat | Fail-closed control |
|---|---|
| Treat authenticated raw request arrival as confirmation | all raw routes remain kernel-ineligible until separate confirmation evidence is present |
| Mint a precondition from the same current read and call the user's old view fresh | require a prior backend-owned expected binding; immediate current reads still enforce invariants but do not prove view freshness |
| Give raw routes weaker idempotency | require the same canonical operation/key/digest semantics before eligibility |
| Alias route names into distinct replay scopes | every raw and confirm variant maps to one canonical operation id per family |
| Disclose an original receipt after authority revocation | current authority and confirmation precede replay disclosure |
| Allow event or Context Frame evidence to authorize a write | neither is accepted as authority, confirmation, freshness or command-success evidence |
| Deadlock mixed legacy and confirm paths | one canonical lock order; mixed execution is forbidden until every participating helper conforms |
| Double-book create without a target row | require a separately reviewed database-owned schedule-domain fence before create convergence |
| Use deprecation to strand a hidden consumer | retirement depends on explicit consumer, import, migration and recovery replacement evidence |
| Mislabel a loser as success | eight closed results; only `committed` owns a first mutation ribbon |
| Replay creates a second mutation audit | replay returns the original receipt plus distinct replay observation only |
| Store sensitive raw command material in audit | minimized digests/references only; no raw bodies, tokens, credentials or patient free text |

## Residual risks deliberately unproved

- production precondition-token cryptography and key rotation;
- exact PostgreSQL create-fence primitive and mixed-lock implementation;
- current raw-route consumer completeness;
- route/helper behavioral parity;
- HTTP status and client-copy migration;
- audit/idempotency persistence and crash recovery;
- RLS and patient-data behavior; and
- deployment, observability and rollback.

These remain outside this provider-free unmounted tranche. The contract is a
design input, not runtime safety evidence.
