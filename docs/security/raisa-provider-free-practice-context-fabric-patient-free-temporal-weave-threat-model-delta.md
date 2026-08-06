# Threat-model delta: Context Fabric patient-free temporal weave

Date: 2026-08-06

Status: bounded provider-free design delta

## Trust boundaries and assets

The active frame set is trusted only because its exact parent proofreader and
digest bindings pass. Candidates and signal envelopes are untrusted. Backend
authority policy, manifest/lease derivation and the deterministic proofreader
are separate trusted controls. No live watcher, database, event feed or source
reader exists in this tranche.

Protected assets are tenant/principal/session isolation, current-truth
freshness, frame-set immutability, event/command separation, ordered
reconciliation, historical integrity, purpose-specific retention and minimal
disclosure.

## Threats and controls

| Threat | Control |
|---|---|
| Event payload is mistaken for replacement truth | Signal schema has no payload/before/after fields; relevant events only invalidate and emit an inert reassembly requirement. |
| A frame is patched mid-turn | Frame-set digest is immutable; lifecycle state is separate and monotonic; recovery requires a new frame-set id/digest and proofreading. |
| Candidate creates watcher/tenant/role authority | Manifest and lease authority fields are backend-derived and absent from the closed candidate; lease execution and returned data are constant false. |
| Cross-practice or cross-session invalidation | Exact practice/session-binding/session-generation/policy/manifest equality before cursor or state processing. |
| Replay or duplicate creates repeated disruption | Deduplication binds event id, lease/generation and frame-set digest; equal/older aggregate revisions are suppressed. |
| Reordered or missing events leave stale context usable | Cursor discontinuity fails closed, retires the old set and requires a new baseline plus fresh authority. |
| Slow reassembly overwrites newer context | Opaque single-use ticket, monotonic request revision, exact generation/grant/manifest binding and stale-result rejection. |
| Lease expiry/revocation races a signal | Expiry/revocation is checked before classification; old set becomes unavailable and no read is executed. |
| Overbroad event family or selector causes ambient invalidation | Event family, frame/source class, location, aggregate, time and sensitivity must be a deterministic intersection of manifest and backend lease. |
| Event-to-command escalation | Signals, decisions and requirements are read-only with no command authority; no command/API/runtime import exists. |
| Historical snapshot is asserted as current truth | Distinct type with valid/transaction time, retention class and constant `current_truth_authority: false`. |
| Correction overwrites historical evidence | Immutable correction/supersession lineage; temporal overlap without lineage fails proofreading. |
| Historical retention becomes ambient practice memory | Purpose, scope, retention class, maximum lookback/count and fields are backend-clipped; no production retention is chosen here. |
| Sensitive event data leaks into evidence | Authored-synthetic opaque refs only; no payload, patient, free text or product-derived values; traces use digests and safe codes. |

## Residual risks deliberately deferred

Live PostgreSQL notification/feed semantics, transactional outbox guarantees,
production cursor recovery, persistent deduplication, retention/deletion jobs,
RLS/ABAC, patient identity, source-specific privacy, real application-session
revocation, operational load, provider prompt minimisation and command safety
require separately authorised descendants.

## Forbidden openings

No patient, clinical, product-derived, historical-PHI or protected data; no raw
audit; no real database/session/feed/listener/service; no persistence,
retention scheduler, broker, worker or dead-letter queue; no provider or
external retrieval; no GraphQL/REST route, resolver, mutation or subscription;
no command/write; no product runtime; no deployment, production, release,
Pages, protected evidence or protected-ref movement. Preserve and exclude
`docs/branding/` and unrelated untracked artifacts.
