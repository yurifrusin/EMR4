# Threat-model delta — status-confirm physical-design architecture

Date: 2026-08-12

Source HEAD: `fad85e038b7168c3323075024dba7f9d5709eff5`

## Scope

This delta covers the unmounted additive state-version, private-receipt and
ordered-transaction design for status confirmation. It is architecture-only
and executes no application or database code.

## Threats and controls

| Threat | Frozen control |
|---|---|
| A timestamp or client value impersonates source identity | PostgreSQL owns a positive `BIGINT` revision starting at one and advances it synchronously on every committed row update. |
| One legacy route forgets to advance the version | The database trigger, not route code, owns the increment. |
| Direct SQL suppresses or chooses a version | The trigger replaces the submitted value with `OLD + 1`; overflow aborts. |
| Backfill invents false historical chronology | Existing appointments receive baseline one only, explicitly labelled as a cutover baseline. |
| Old idempotency rows are mistaken for safe receipts | `completed_receipt_version IS NULL` remains legacy and is never inferred or replayed as v1. |
| Raw session identifiers become durable | Store only a domain-separated 32-byte HMAC digest; never store the secret or raw session in the v1 receipt. |
| JSONB replay changes bytes | Store the exact canonical UTF-8 response bytes and deliver them directly for initial response and replay. |
| Stored bytes are corrupted | Verify the existing SHA-256 digest in constant time before replay and release no body on mismatch. |
| Target enumeration leaks through idempotency | Stop target absence before idempotency access; current authority precedes every classification or disclosure. |
| Concurrent commands create multiple effects | Hold practice, appointment and idempotency locks in one order and commit mutation, audit and completed receipt atomically. |
| Practice suspension crosses an in-flight command | Lock the practice row `FOR SHARE` before the appointment; practice updates/deletion wait. |
| Lock policy drops work or spins | Forbid `NOWAIT`, `SKIP LOCKED` and hidden effect retry; use one positive bounded wait and return a generic rolled-back/transient outcome. |
| New private fields leak through the API | Keep the closed public OpenAPI result unchanged; private receipt fields have no response mapping. |
| Trigger is mistaken for watcher/event authority | Label it only as a synchronous row invariant; it emits no event, cue or command. |
| Automatic downgrade erases used receipt meaning | Allow rollback only before first runtime use; afterwards require forward recovery. |
| Protected evidence is rediscovered | Exact-file allowlist only; AER-0292 forbids directory-root content and filename-metadata discovery. |

## Residual risks

This architecture does not prove executable Alembic lowering, PostgreSQL
catalogue behavior, trigger behavior, ORM mappings, service composition,
actual lock waits/deadlocks, mounted-route compatibility, restart or
unknown-commit recovery, performance, retention or operational rollout.

`READ COMMITTED` deliberately gives concurrent commands or revocations a
database order; it does not promise that every arriving request wins. Safety is
the single atomic committed truth and non-disclosure to losers.

## Authority boundary

No application/model/migration/service/route edit or import, executable DDL,
database/SQL/real lock, provider/ADC/credential action, product/patient data,
watcher/event, product command, deployment, production, release, Pages or
protected-ref action is opened. `docs/branding/` and all unrelated untracked
paths remain excluded.
