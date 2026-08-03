# Threat-model delta: Davida default-location command boundary

Date: 2026-08-03

Status: architecture-only, provider-free, non-executing

## Boundary

This tranche documents, but does not mount or implement, a future backend-owned
REST proposal-to-confirm path for one practitioner default-location change.
Davida remains a non-authoritative proposal source. The backend remains the
sole identity, authorization, concurrency, confirmation, write and audit owner.

| Threat | Required control | Failure outcome |
|---|---|---|
| Resource enumeration before authorization | Authenticate and authorize practice/action before resource lookup; uniform denial | `unauthenticated` or anti-enumerating `not_authorized` |
| Body actor/practice/role is treated as authority | Derive all three from the authenticated application session; body values are binding assertions that must exact-match | `practice_scope_mismatch` or `confirmer_not_authorized` before disclosure |
| Davida or another agent confirms | Future contract permits only authenticated `human_user`; role is exactly practice manager/owner; backend-issued evidence. This is not a current permission-matrix runtime grant. | `confirmer_not_authorized` |
| Cross-practice confused deputy | Exact practice binding in session, proposal, aggregate lookup, location lookup, idempotency scope, audit and outbox | `practice_scope_mismatch` with no resource disclosure |
| Stale dry run becomes command | Recompute current before/after state; bind dry-run/context revision, expected aggregate version and hashes | `proposal_stale` or `aggregate_version_mismatch` |
| Client extends proposal life | Server expiry is the minimum of dry-run expiry and backend time plus 120 seconds; half-open comparison | `proposal_expired` |
| Proposal/body tampering | Canonical deterministic proposal and request hashes; extra-forbid typed envelopes | `proposal_hash_mismatch` or schema rejection |
| Role revoked between admission and write | Reauthorize exact practice/action/resource inside the transaction immediately before mutation | `not_authorized`, whole transaction rolled back |
| Same key performs different action | Durable scope + canonical fingerprint binding | `idempotency_conflict` |
| Same command is retried | Return stored bounded receipt for exact key/fingerprint; no second write/event | Exact prior domain receipt, zero new effects |
| A signed self-contained proposal implies a hidden proposal store | `proposal_id` is backend-issued, signed and self-contained; verification requires no proposal row or reservation | Acceptance failure |
| Client mints confirmation evidence from structured fields | Request accepts only an opaque backend-issued server-held one-use evidence reference; server record owns covered hashes and nonce | `confirmation_evidence_invalid` |
| Consumed evidence is reused under another key | Unique single-use confirmation-evidence nonce guard in the confirmation transaction | `confirmation_replay_rejected` |
| Concurrent updates overwrite each other | Lock target and compare expected aggregate version plus before-state hash | `aggregate_version_mismatch` or `before_state_conflict` |
| Inactive/foreign location is assigned | Same-practice active-location check inside the command transaction | `location_not_active` or anti-enumerating scope rejection |
| Audit/outbox diverges from aggregate | One transaction covers aggregate, version, audit, outbox and idempotency completion | Full rollback; no receipt or publishable event |
| Event publishes before durable truth | Transactional outbox; dispatcher may publish committed rows only | No pre-commit publication |
| Receipt leaks identity or practice data | Opaque references/hashes, closed booleans/codes, no display names or free text | Acceptance failure |
| Documentation is mistaken for runtime authority | `.invalid` server, architecture-only extensions, static absence checks for route/model/migration/service code | No runtime claim; actual implementation remains gated |
| Branding enters evidence | Exact-path checks exclude `docs/branding/` | Acceptance/integration gate fails |

## Residual gates

No FastAPI route, `app.main` import, migration, model, database service, write,
event publisher, provider/model, memory/RAG, real identity/data,
patient/clinical/document data, arbitrary API access, GraphQL mutation,
deployment, production, release, protected evidence/ref or branding authority
is established. Actual administrative command implementation is a material
Yuri-owned gate.
