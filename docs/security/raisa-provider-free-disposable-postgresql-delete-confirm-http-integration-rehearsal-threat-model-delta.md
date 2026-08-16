# Threat-model delta — disposable PostgreSQL delete-confirm HTTP integration rehearsal

Date: 2026-08-17

Timestamp: 2026-08-17T07:05:13.9032501+10:00 (Australia/Brisbane)

Status: frozen

Reasoning level: Extra High

## Scope

This delta covers one provider-free, authored-synthetic, local FastAPI HTTP
integration rehearsal of appointment delete confirmation over one owned
disposable PostgreSQL 16 server. It also covers the two exact preconditions
proved before execution: producer/adapter canonicalization parity and
transaction-local tenant context in the command-owned session.

It changes no public command meaning, API schema, adapter admission,
composition, migration, receipt contract or raw compatibility DELETE.

## Assets and trust boundaries

- server-authenticated practice, user, role and authority generation;
- signed proposal evidence and its opaque positive source-version binding;
- normalized cancel capability grant;
- appointment row, database-owned adjacent state version and waiting-area
  state;
- idempotency record, private canonical receipt and attributable delete audit;
- strict public receipt projection; and
- one owned container/network/relay lifecycle and sanitized evidence artifact.

The HTTP client may carry proposal evidence and acknowledgement but cannot
mint identity, practice, authority generation, capability, version, session,
receipt or audit truth.

## Threats and required controls

| Threat | Required control |
|---|---|
| Divergent route and adapter canonicalization makes valid evidence unusable or admits ambiguous material | route helpers delegate to the accepted adapter command, freshness and signed-payload helpers; a pure cross-seam regression requires `verified`/`exact` ingress |
| Fresh command session has no tenant context or inherits stale pooled context | physical transaction sets the UUID-normalized authenticated practice with transaction-local `set_config` after isolation and before reads; two-pool postflight requires the setting absent |
| Client selects or alters practice, generation, capability or source version | practice/user/generation come from verified server identity and database rows; capability and version are rechecked under locks; binding tamper stops before a command session |
| Cross-practice existence disclosure | forced RLS plus practice-qualified locked lookup returns the same typed unavailable result and releases no row detail |
| Revoked or absent capability commits | normalized grant default denial and two current-authority checks precede effect; revocation scenarios require zero effect |
| Lost response repeats cancellation | database-owned idempotency identity and exact stored private receipt permit replay with no second appointment/audit/receipt effect |
| Private receipt reaches HTTP | the route canonicalizes only the strict public projection; evidence stores hashes/counts only and asserts public bytes differ from private stored bytes |
| Missing warning acknowledgement clears waiting area | exact warning-set equality is checked before effect and again against locked state; mismatch rolls back |
| Partial appointment/audit/receipt write | one database transaction and reciprocal completeness constraints; forced adjacent-version-trigger failure must return closed 503 and roll back all effects |
| Disposable runtime escapes or cleanup deletes unrelated resources | internal network, no port publishing, fixed loopback relay, tmpfs, bounded resources, exact nonce/label/name/ID/image ownership checks and exact-ID absence postflight |
| Evidence leaks secrets, PHI-like rows or raw runtime identifiers | fixed authored-synthetic inputs only; released schema forbids tokens, HMACs, bodies, private bytes, SQL, URLs, passwords, runtime IDs, row values and raw exception text |
| Rehearsal silently broadens product authority | no product database, reusable route capability, raw DELETE, provider, UI, deployment, release, Pages or protected-ref action; exact source allowlist and hostile contract mutations fail closed |

## Deliberately unproved

Concurrency beyond the existing database locks, restart/crash, unknown commit,
operational retention, performance, visible client behavior, product or
patient data, real identity, external adapter use, deployment and production
remain outside this delta.

## Recovery

Any source-hash mismatch, contract mutation admission, wrong database role,
RLS absence, scenario failure, evidence-schema failure or incomplete cleanup
produces failure evidence without raw details and forbids Gemini review or
acceptance. Mechanical harness failure may receive one bounded correction. A
need to change command meaning, adapter/composition/schema/migration or a
closed authority surface requires a new diagnosed boundary rather than silent
expansion.
