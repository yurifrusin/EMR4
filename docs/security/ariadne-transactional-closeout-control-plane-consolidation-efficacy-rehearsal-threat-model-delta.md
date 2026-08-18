# Threat-model delta — Ariadne transactional closeout control-plane consolidation efficacy rehearsal

Date: 2026-08-19

Timestamp: 2026-08-19T00:31:10.3800847+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `f21072405a4d5877ec03e2cd1aefc7fa74d379e9`

## Scope

This delta covers only the provider-free repository-local typed closeout
journal, deterministic reducer, shadow generation publisher, efficacy harness
and optional DeepSeek broker WorkOrder/event-clock binding. It opens no product,
data, provider, credential, deployment or protected-ref surface.

## Assets and trust boundaries

Protected assets are the exact accepted Git lineage, live latch, Continuity
graph, Compass, current report, agent-error aggregate, authority boundaries,
untracked user files and the broker's existing capability/provider-key
separation. The new trust boundaries are manifest-to-reducer,
reducer-to-shadow-generation and WorkOrder-to-broker-event-stream.

The journal is candidate control-plane evidence, not product truth. Wall-clock
timestamps are metadata; the hash-chained sequence is the causal clock.

## Threats and mandatory controls

| ID | Threat | Mandatory control and proof |
|---|---|---|
| TCP-001 | A graph, Compass, report or latch projection is written before another projection fails validation. | Reduce and validate all projections in memory, stage privately, reread hashes, then publish one shadow directory rename; fault injection leaves no published partial. |
| TCP-002 | A short, stale, foreign or hand-copied Git ID binds the closeout. | Manifest admits only `source_anchor: current_head`; fixed Git snapshot obtains the full ID and the strict existing commit resolver verifies it. Extra source fields fail exact-key validation. |
| TCP-003 | Journal events are dropped, duplicated, reordered, replayed or altered. | Contiguous sequence, operation/transaction binding, prior digest and canonical event digest on every event; validate the entire chain before projection or publication. |
| TCP-004 | The DeepSeek broker advances an independent or forged clock. | Strict opt-in WorkOrder plus an independently supplied canonical WorkOrder digest bind journal, sequence anchor, source, authority, lease, branch/worktree and tool set; every broker event continues that chain and Python independently validates it. |
| TCP-005 | A WorkOrder silently broadens tools, provider posture, product/data scope or authority. | Exact keys, exact `edit/glob/read` set, authority/forbidden-surface digests, independently matched whole-WorkOrder digest and provider-free rehearsal posture; mismatch rejects startup or request before upstream I/O. |
| TCP-006 | Derived counts, cutoffs, peers, revisions or retry totals drift because they are copied into several files. | Reducer derives them once from journal/incident inputs; caller-supplied derived fields are forbidden and peer symmetry is validated. |
| TCP-007 | Shadow rehearsal mutates live authority or user-owned files. | Canonical authority paths, `.git`, product sources and paths outside an explicit shadow root are denied; tests hash live files across success and injected failure; preserve `docs/branding/`. |
| TCP-008 | Efficacy is claimed by excluding shared-engine cost, weakening coverage or using flattering fixtures. | Frozen three-fixture baseline, seven observed defect classes, exact physical-line/file accounting, raw growth plus amortised cost, zero escapes and no coverage loss. Calculations are derived, not supplied. |
| TCP-009 | Timing noise or wall-clock skew changes causal order or admission. | Causal sequence alone decides order; alternating repeated monotonic timings are informational and cannot pass or fail correctness. |
| TCP-010 | A passing shadow is treated as live replacement, occupied provider authority or production readiness. | Claim remains repository-local and shadow-only; existing controls are not retired; occupied Harness/HMR/provider, product, deployment and protected refs remain closed. |
| TCP-011 | Broker logs leak capability tokens, provider keys or prompt/product content through the new clock fields. | WorkOrder/event fields are identifiers and digests only; retain existing secret substitution and no-secret log tests; no raw message body enters clock metadata. |
| TCP-012 | A stale latch or asymmetric incident relationship survives as a valid projection. | Exact live-operation match, typed transition, derived aggregate and bidirectional peer validation occur before publication; hostile fixtures fail closed. |

## Abuse and failure cases

Tests must cover unknown keys, abbreviated IDs, wrong branch/worktree, wrong
protected commit, stale operation, sequence gaps/replay, wrong prior/event
digest, altered payload, non-symmetric peers, stale cutoff/count, boundary text
substitution, nonallowlisted tools, wrong WorkOrder identity, publication-path
escape, prevalidation write attempts and an injected exception after each
staging write.

No failure may trigger a provider call, canonical authority write, Git
operation other than fixed read-only inspection, product import, application
route, database, browser, credential operation or retry of the native Harness.

## Residual risk and claim boundary

Directory publication is rehearsed only under a disposable shadow root. This
does not prove a crash-atomic migration of the existing independently addressed
live authority files; that requires a later measured adoption design. The
native Harness stock-headless HMR terminal remains unresolved. A conformant
WorkOrder/event chain proves traceability and authority binding, not worker
reasoning quality or completion reliability.

No protected holdout, historical diary, product/patient/clinical data, live
provider, production runtime, deployment, release, Pages or protected-ref
movement is authorised.
