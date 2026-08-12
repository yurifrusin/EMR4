# Threat-model delta: default-off shadow comparison

Date: 2026-08-12

Status: `provider_free_unmounted_static_architecture`

## Assets protected

- authoritative request/response and transaction behavior;
- command authority, confirmation, freshness and idempotency boundaries;
- patient and product identifiers and free text;
- audit/receipt meaning and route provenance; and
- default-off configuration integrity.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Observer becomes an enforcement gate | primary result is sealed first and there is no return edge |
| One flag silently enables observation | immutable generation, global, practice and exact-route controls must intersect |
| Stale or unknown configuration is reused | missing/unknown/stale/superseded/revoked generation denies |
| Kill switch accidentally enables | external control is disable-only within a generation |
| Raw request or patient data enters diagnostics | closed digest projection excludes bodies, direct IDs, free text and tokens |
| Shadow candidate reaches command service | distinct non-executable type and no kernel/command capability |
| Observer failure changes the HTTP result | failure, timeout, overflow and sink error only drop diagnostic evidence |
| Record is mistaken for audit or truth | record declares diagnostic-only, lossy, non-authoritative and no retention selected |
| Gap comparison grants route eligibility | comparison cannot change the parent `current_raw_not_kernel_eligible` posture |
| Shadowing hides response changes | headers, status, body, transaction and audit are immutable before admission |

## Residual boundary

This static architecture does not prove an application hook, concurrency,
latency isolation, memory bounds, privacy-safe production hashing, aggregation,
retention, operational monitoring or rollback. Those require later separately
accepted evidence.
