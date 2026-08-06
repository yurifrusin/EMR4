# Practice Context Fabric and Bureau Memory Bank contract design

Date: 2026-08-06

Status: provider-free authored-synthetic contract design

## Pipeline

`ContextNeedCandidate` is model-shaped but non-authoritative. Trusted backend
code supplies `ContextAuthorityBinding`; `ContextNeed` binds both by digest.
The scope service intersects every requested dimension with backend policy and
emits an expiring `ContextScopeGrant`. The assembler selects only permitted
authored-synthetic recent-work items, builds one immutable memory frame and
records selector and weave traces. The proofreader sees the same packet and
recomputes its bindings before release.

No stage infers a principal, practice, role, consent, retention period or
command authority from the candidate.

## Contract objects

- `ContextNeedCandidate`: request id, Bureau, purpose, frame/source classes,
  entity features, named temporal hint, requested half-open interval, fields,
  result/freshness bounds and the constant false command ceiling.
- `ContextAuthorityBinding`: backend principal, roles, practice, locations,
  session and policy allowances, issued/expiry times and digest.
- `ContextNeed`: exact candidate/binding digests and assembly time.
- `ContextScopeGrant`: deterministic intersection, reductions, expiry,
  byte/result bounds and constant read-only/no-provider/no-command ceilings.
- `BureauMemorySelector`: allowlisted Bureaus, action families, actor relations,
  outcomes, temporal hint, maximum results and a canonical selector digest. It
  has no free-text, wildcard, actor-id, audit, SQL or cursor expression.
- `BureauMemoryItem`: bounded historical reference with relation, coded
  outcome, opaque target reference when allowed, receipt/revision/digest,
  completion time and `authority_ceiling: read_context_only`.
- `ContextFrame` and `ContextFrameSet`: source-labelled, purpose/practice-bound,
  expiring projections with provenance, redaction, supersession and digests.
- selector, weave and proofreader traces: deterministic rules, reductions,
  exact input/output digests and closed release disposition.

## Memory versus audit

The audit ledger remains complete, immutable and compliance-oriented. The
Memory Bank is derived, lossy, minimal, purpose-filtered, expiring and
rebuildable. A Bureau never queries or receives raw audit rows. Memory items
are historical references only; correction rebuilds or omits a projection.

`bureau_memory_item_set` is a frame type under `recent_collective_work`, not a
new authoritative source class and not a standalone API.

## Deterministic rules

- Canonical UTF-8 JSON with sorted keys and SHA-256 binds every object.
- Intervals are UTC half-open `[start, end)` and effective scope is
  `max(starts), min(ends)`.
- Lists are stable intersections in candidate order; limits are the minimum.
- Items match every allowed dimension, fall inside the effective interval and
  are not superseded. They sort by completion descending then item id ascending.
- Requestable disclosure fields are closed to the bounded request label and
  optional opaque target reference; the latter is removed when policy narrows it.
- Result count and canonical item-byte ceilings are both applied before weaving.
- Expiry never exceeds binding, grant, source-freshness or policy expiry.
- Any empty mandatory intersection returns one generic `NOT_AVAILABLE`
  disposition; detailed protected reductions remain in the trace.
- Proofreading revalidates the exact need, grant, selector, selector trace,
  weave and frame-set digests seen by the Bureau, then rechecks item scope,
  expiry, supersession, minimisation, cardinality and byte ceilings.

## API Spine

`practiceContextFabric(candidate: ContextNeedCandidateInput!): ContextFrameSet!`
is an unmounted documentation extension of the existing read graph. Candidate
input excludes principal, roles, practice, locations, consent and authority.
There is no Memory Bank root, mutation, subscription, resolver or route.
Future actions remain separate REST/OpenAPI commands with fresh backend
authorization, confirmation, idempotency, audit and readback.

## Claim boundary

This contract can prove deterministic provider-free component behavior only.
It does not prove a model-required Bureau turn, product data retrieval,
real-world identity matching, privacy policy adequacy, persistence, retention,
clinical reasoning, runtime wiring, commands, deployment or production.

Acceptance evidence binds the exact contract, API document, plan, design,
threat delta, engine, acceptance generator and focused test by canonical-LF
byte hash, so Windows checkout line endings cannot change the result. It
does not embed the containing Git commit as a self-reference: the independent
review receipt binds the final exact HEAD after commit, while the evidence file
remains reproducible before and after that commit.
