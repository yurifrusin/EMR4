# Threat-model delta: unmounted Rayleen invalidation/reassembly seam

Date: 2026-08-06

Status: frozen bounded provider-free design delta

## Trust boundaries and assets

The original A4 frame, backend authority binding, scope grant and alias manifest
are authoritative only within the accepted authored-synthetic fixture. Adapter
results, packets, signals and reassembly instructions are untrusted until full
deterministic reconstruction and same-packet proofreading pass.

Protected assets are practice/session/grant isolation, adapter provenance,
source/frame/dependency integrity, immutable old context, event/truth
separation, monotonic invalidation, stale-result rejection and the absence of
read, provider or command authority.

## Threats and controls

| Threat | Control |
|---|---|
| A resealed adapter result is detached from its source | Sole extractor reruns the adapter from authoritative inputs; seam proofreader reconstructs the entire chain and requires canonical equality. |
| Adapted envelope and waiting frame diverge | Exact source id/revision/digest and waiting frame id/digest are sealed into one binding trace and rechecked against the dependency manifest. |
| Event metadata becomes replacement truth | Signal schema has no payload/before/after/replacement fields; temporal processor only retires context and emits an inert requirement. |
| Signal impact is narrowed to hide another stale frame | Accepted processor determines intersections; seam requires the waiting dependency but preserves every additional affected dependency. |
| Old frame set is patched or restored | Before/after canonical digest equality, monotonic state, `frames_mutated: false`, and no new-frame admission in this tranche. |
| Reassembly requirement becomes an executable capability | Instruction contains fixed labels only; execution, returned-data, command and provider flags are false; no callback, route, credential or source reader exists. |
| Requirement silently reuses expired authority | Exact grant, binding, manifest, lease, session generation, request revision and expiry are bound; the future sequence begins with a fresh authority check. |
| Slow result overwrites newer context | Accepted stale-request assessor rejects an older request revision; no result is admitted here. |
| Cross-practice or cross-session signal causes invalidation | Accepted temporal manifest/lease derivation and signal classifier require exact practice, session, generation and policy bindings before state change. |
| Duplicate/replayed signal emits multiple requirements | Accepted checkpoint, revision and replay controls plus exactly-one requirement assertion. |
| Evidence claims a live watcher or fresh read | Static zero-surface checks and strict provider-free/unmounted evidence label; instruction records `source_read_executed: false`. |
| Command or provider authority enters through composition | Closed schemas, fixed false ceilings, no `app/**`, route, OpenAPI, provider or runtime imports, and inherited API Spine tests. |

## Residual risks deliberately deferred

Real PostgreSQL/outbox/feed delivery, transaction ordering, persistent
checkpoints, restart recovery, RLS/ABAC, operational deduplication, genuine
source authorization, patient privacy, load, retention, provider context use and
command safety require separately frozen descendants.

## Forbidden openings

No patient, clinical, financial, product-derived, historical-PHI or protected
data; no raw audit; no live database/session/feed/watcher/listener/source reader;
no persistence, broker, background worker or retention scheduler; no provider
or external retrieval; no GraphQL/REST route, resolver, mutation or subscription;
no command/write; no product runtime; no deployment, production, release, Pages,
protected evidence or protected-ref movement. Preserve and exclude
`docs/branding/` and unrelated untracked artifacts.
