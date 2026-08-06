# Threat-model delta: unmounted authored-synthetic observation-to-temporal-signal rehearsal

Date: 2026-08-06

Status: frozen provider-free implementation delta

## Trust boundary

Source-shaped metadata is untrusted. Policy, binding, alias registry, impact
policy, clock, synthetic activation and HMAC key are backend-owned inputs whose
canonical values must be reconstructed by the proofreader. The emitted temporal
signal remains control metadata, not context truth or authority.

## Threats and controls

| Threat | Control |
|---|---|
| Source payload or PHI is smuggled as metadata | Recursively closed input; no selectors, field lists, correlations, reason text, people, practitioners, locations, timeslots, callbacks or arbitrary strings; unknown fields block. |
| Raw event id becomes a semantic identifier or leaks | Exact non-semantic source-contract grammar; domain-separated HMAC-SHA-256; raw id and key absent from every output/error/evidence value. |
| Hashing or aliasing legitimises prohibited content | Prohibition is semantic as well as structural; only backend-issued registered aliases resolve and arbitrary source strings cannot enter the admitted object. |
| Source narrows invalidation | Source input has no impact field; non-empty backend event/schema/aggregate floor is unioned with registry impact. |
| Unknown impact becomes silent irrelevance | Return bounded `FULL_INVALIDATION_REQUIRED`; emit no ordinary signal and never classify as `IRRELEVANT`. |
| Disabled policy is bypassed by a test fixture | Exact sealed synthetic activation is mandatory, expiry-bound, live-ineligible and fixes every connection/effect/authority flag false; policy stays disabled. |
| Integration principal inherits session or read power | Distinct observer binding type with return/read/provider/command/persistence false; no `ContextAuthorityBinding` or read grant is accepted. |
| Bool passes as an integer coordinate | Explicit type checks exclude bool and enforce `1..9007199254740991`. |
| Wall-clock time claims stream completeness | Transaction position and expected predecessor govern admission; source time is skew-bounded metadata only. |
| Duplicate/replay renews authority or advances state | Pure closed decision with no mutation; no lease, activation or binding is renewed. |
| Gap/revision uncertainty is guessed through | `FULL_INVALIDATION_REQUIRED`; no signal/checkpoint advancement or current-context continuation claim. |
| Registry substitution crosses a valid seal | Exact registry digest and practice/source/class bindings are reconstructed and compared in the same packet. |
| Impact policy is self-consistently replaced | Exact policy id/digest and non-empty mandatory floor are reconstructed by the proofreader. |
| Temporal signal is source-supplied | Only trusted code may call the accepted constructor after admission; supplied signals are not inputs. |
| Signal becomes replacement truth or a read trigger | Accepted temporal engine can only retire context and emit an inert requirement; source read and returned data remain false. |
| Checkpoint evidence is overstated | Design-time continuity requirement fixes `checkpoint_persisted: false`; no filesystem/database state exists. |
| Test key appears in receipts or errors | Key remains an in-memory argument; evidence checks recursively prohibit it and the raw event id. |
| Pure module gains runtime side effects | Static/runtime spies block filesystem writes, network, database, subprocess, provider, source, listener and command surfaces. |
| Packet is called live evidence | Exact provider-free unmounted authored-synthetic evidence label and narrow claim boundary. |

## Residual risks deliberately deferred

Real source identity and authentication, PostgreSQL/outbox choice, monotonic
transaction position, database isolation, atomic checkpointing, crash/restart,
retention, RLS/ABAC, backpressure, operational audit, source-family semantics,
deployment and privacy review require a separately frozen source-specific
descendant.

## Forbidden openings

No protected evidence, historical PHI, patient/clinical/financial/product data,
raw audit, source/database/feed/watcher/listener, checkpoint/persistence,
provider/external retrieval, API/app route, GraphQL/REST mutation, command,
runtime, deployment, production, release, Pages or protected-ref movement.
Preserve and exclude `docs/branding/` and unrelated untracked artifacts.
