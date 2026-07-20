# Reception One committed-event runtime threat-model delta

**Status:** frozen for bounded local implementation  
**Date:** 2026-07-21  
**Parent controls:** `docs/security/bernie-stage2-threat-model-delta.md` and the API Spine security baseline  
**Authorized event:** `diary.appointment_rescheduled` only

## Scope

This delta covers one provider-free, authored-synthetic, loopback event path:

`existing signed update confirmation -> same-transaction append-only event -> authenticated practice-scoped polling -> fresh Diary reads -> quiet Reception One cue`

It grants no new appointment command, provider, PII, GraphQL mutation or subscription, external broker, production, deployment, release, Stage 3B, voice, or autonomous-action authority.

## Protected assets and trust boundaries

- PostgreSQL remains authoritative for appointments, audits, idempotency, and the new committed-event row.
- The signed update-confirm route remains the only producer entry point.
- The committed-event table is a minimal signal store, not a second clinical record.
- The authenticated read route crosses the database-to-browser boundary and must apply both application practice filtering and forced PostgreSQL RLS.
- Browser attention state is memory-only and untrusted; every patient-bearing result comes from fresh authorized appointment/projection reads.
- Protected holdouts, historical Diary material, real PII, providers, cloud transports, and production configuration stay outside the tranche.

## Threats, controls, and mandatory evidence

| Threat | Required control | Acceptance evidence |
|---|---|---|
| Event visible before appointment commit, or appointment commits without its event | Appointment, update audit, idempotency completion, and event insert share one database transaction and one final commit | Success correlation plus injected rollback test |
| Duplicate event on command retry | Existing idempotency claim/replay owns the command; unique event id and unique aggregate/revision constraints provide defence in depth | Same key and same fingerprint replay creates no second audit or event |
| Reordered, replayed, expired, or superseded delivery | Deterministic order, signed opaque time/event cursor, 24-hour eligibility, event-id deduplication, and monotonic per-appointment revision | Cursor/order/expiry tests and repeat-poll browser evidence |
| Cross-practice event or cursor disclosure | Authenticated internal staff, explicit practice predicate, composite practice keys, forced RLS, and practice-bound cursor signature; foreign/unknown cursors re-baseline without history | Two-practice route and direct RLS tests |
| Forged or schema-downgraded event | Fixed event type and schema version, allowlisted payload schema, database constraints, and consumer rejection of unsupported shape/version | Model/service validation and malformed-row tests |
| Event store becomes secondary PHI/free-text store | Payload allowlist contains only appointment/practitioner/location/time/reason codes; no patient identifier/name, appointment reason/notes, raw instruction, or provider content | Serializer/store tests inspect exact keys and reject extras |
| Client trusts stale or injected payload | Event is only a signal; client requires active-projection membership and fresh appointment plus exact projection reads before a cue | Browser network trace and stale/irrelevant unit cases |
| Event feed becomes a command tunnel | GET-only route, no ack endpoint, no event-driven command call, and client bridge exposes only reads | Router/OpenAPI inspection and mutation-route network allowlist |
| Alert flooding or covert attention capture | One non-modal polite cue, no autofocus/speech, bounded delivered set, coalescing, dismiss, five-minute snooze, and mute-until-reload | Keyboard/attention browser evidence and bounded-state tests |
| Shared-screen disclosure | Patient-free live region; privacy mode masks time comparison and changed-item detail | Smartphone/desktop privacy screenshots and assertions |
| Correlation loss | Event stores command and update-audit coordinates; idempotency completion stores the audit id; appointment/audit/command/event are read back together | Exact PostgreSQL correlation evidence |
| Tampering with event history | Forced RLS plus database trigger rejects UPDATE and DELETE | Direct SQL mutation tests |
| Historical notice disclosure on first load or lost first event when history is empty | Cursorless request mints a signed current-time baseline without writing and returns no historical events; invalid/foreign/expired cursor also re-baselines | Empty-history, feed-baseline, and cursor tests |

## Residual risks and bounded posture

- Polling is a local proof mechanism, not a production delivery architecture. It may add bounded latency and remains disabled by default.
- The event row retains backend actor, command, and audit identifiers for correlation; the browser response omits them. Production retention, encryption, and operational access remain closed.
- In-memory mute and snooze reset on reload by design. Persistent preferences are not authorized.
- Database append-only enforcement protects ordinary runtime roles, but privileged database administrators remain outside the application threat boundary.
- Aggregate revision is derived from the serialized append-only appointment audit sequence in the locked update transaction. A different cross-service event source would require a new revision design and fresh approval.

## Stop conditions

Stop and return to Yuri if implementation requires another event family, patient data in an event, a new mutation, an external transport, persistent attention state, a retention worker, production settings, a provider, real users/data, or broader relevance inference.
