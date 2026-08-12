# Threat-model delta: unmounted conditional-command admission rehearsal

Date: 2026-08-12

Status: `provider_free_unmounted`

## Threats exercised

| Threat | Rehearsal control |
|---|---|
| Client widens token scope | exact token/request binding comparison and closed schema |
| Expired or unauthentic token proceeds | structural admission rejection before outcome evaluation |
| Create omits serialization because no row exists | exact schedule-domain fence and lock-plan requirement |
| Lock order permits future deadlock drift | exact operation projection of the canonical global order |
| Revoked actor receives a replay receipt | current authority precedes idempotency evaluation |
| Freshness is treated as confirmation | distinct confirmation policy and evidence fields |
| Retry creates another effect | same-digest replay returns the original synthetic receipt identity |
| Key reused for a changed command | different digest yields non-mutating `idempotency_conflict` |
| Event claims truth or success | packet rejected before command evaluation |
| Rehearsal result is mistaken for execution | `effect_performed` is always false; only a planned flag exists |

## Residual risks

The rehearsal does not verify production cryptography, key rotation, database
locks or constraints, RLS, route integration, HTTP error disclosure, real
idempotency storage, audit persistence, watcher availability, performance or
patient-data handling. Those remain separate descendants.

## Closed authority

No route, database/source, event, watcher, provider, patient/product data,
credential, executable, command/write, deployment, release, Pages or protected
ref is opened.
