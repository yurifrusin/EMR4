# Threat-model delta — status-confirm physical schema-and-transaction scaffold

Date: 2026-08-12

Source HEAD: `a30db2e8bfcb6b067b55985cabf2e6200906f182`

## Scope

This delta covers additive ORM mapping, one inert migration, pure receipt
helpers and an unmounted ordered-lock seam. It covers source representability,
not executable PostgreSQL behavior or mounted command safety.

## Threats and controls

| Threat | Frozen control |
|---|---|
| App code chooses or suppresses a revision | A database `BEFORE UPDATE` trigger overwrites every submitted version with `OLD + 1`; the ORM only maps the value. |
| Cutover fabricates chronology | Existing rows receive baseline one only, after a nullable/no-default add. |
| Overflow silently wraps | The trigger raises at `9223372036854775807`; positive-range constraints fail closed. |
| Legacy receipts acquire new meaning | All five fields remain null and no legacy row is backfilled or replayed as v1. |
| Raw session identity is retained | Only a domain-separated length-framed 32-byte HMAC helper is supplied. |
| Response replay changes bytes | Exact canonical bytes are stored/delivered; JSONB is inspection-only and integrity is checked in constant time. |
| Receipt fields leak publicly | OpenAPI is unchanged and no route imports the new helper. |
| Target/idempotency probing discloses state | Practice and appointment locks plus first authority check precede idempotency access; a second check precedes classification. |
| Lock shortcuts break ordering | The seam fixes share/update/update order, one bounded wait and excludes NOWAIT/SKIP LOCKED. |
| Scaffold becomes a command accidentally | It does not mutate an appointment, create audit evidence, complete a receipt or mount into a route. |
| Migration is mistaken for verified behavior | DDL remains inert and receives only static verification in this tranche. |
| Downgrade erases adopted meaning | Downgrade raises when any receipt version one exists. |
| Protected evidence is rediscovered | Exact-file allowlist only; one revision-ID-only Alembic head query is the sole metadata exception. |

## Residual risks

PostgreSQL parsing/catalogues, trigger execution, actual row locks and waits,
concurrency, rollback, restart, unknown commit, ORM/database compatibility,
mounted-route behavior, performance and operational rollout remain unproved.
The unmounted seam is intentionally incomplete for writes and cannot itself
complete the atomic mutation/audit/receipt set.

## Authority boundary

No route/database/migration execution, product/patient data, provider/ADC or
credential activity, network, watcher/event, product command, deployment,
production, release, Pages or protected-ref action is opened. `docs/branding/`
and all unrelated untracked paths remain excluded.
