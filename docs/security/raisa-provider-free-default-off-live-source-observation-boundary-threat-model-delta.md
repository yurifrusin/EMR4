# Threat-model delta: default-off live-source observation boundary

Date: 2026-08-06

Status: frozen provider-free architecture-only delta

## Trust boundaries and assets

Untrusted inputs are source metadata, claimed principal/source/practice,
event/schema identity, aggregate and cursor coordinates, timestamps, selectors,
reason codes, policy/binding copies and any restart/recovery claim.

Protected assets are practice and session isolation, immutable Current frame
generations, source/event separation, observer/read/command authority
separation, monotonic invalidation, continuity-gap visibility, checkpoint
integrity, audit minimization and the absence of patient/product payloads.

## Threats and controls

| Threat | Control |
|---|---|
| Observer metadata is treated as current truth | Closed payload-free envelope; event only invalidates; replacement data requires a fresh separately authorized source read and same-packet proofreader. |
| Disabled observer still connects, acquires credentials or advances state | Disabled means zero connection, credential acquisition, admission, cursor movement and read request. |
| Existing Diary feed silently becomes the Context Fabric watcher | Independent default-off policy, integration-principal binding, observer generation, baseline and runtime gate; no inherited enablement. |
| Foreign practice or source poisons cursor state | Authenticate and verify principal/practice/source/policy before deduplication, cursor or aggregate revision processing. |
| Integration principal acquires user/session or read authority | Separate principal and binding types; observer binding fixes data-return/read/provider/command authority false and is ineligible for `ContextAuthorityBinding`. |
| PHI or product truth is smuggled as metadata | Recursively closed fields and exact types; reject arbitrary payloads, free text, direct identifiers, before/after values and hashes/aliases of prohibited content. |
| Event supplies a convenient dependency list to narrow impact | Derive impact only from the sealed manifest; unknown impact blocks or causes bounded full invalidation without widening access. |
| Backdated event disappears behind wall-clock cursor | Require monotonic transaction/outbox position; occurrence/receipt times never prove completeness. |
| Duplicate or replay renews state or authority | Stable identity plus observer generation, stream position and aggregate revision deduplication; suppression cannot renew any binding or lease. |
| Cursor/revision gap is silently ignored | Full invalidation, explicit coverage-gap reason and new baseline; never replay payloads or interpolate truth. |
| Observer starts after frames and misses a change | Establish baseline before binding a new frame generation; otherwise invalidate existing frames and rebuild. |
| Crash separates cursor advancement from invalidation | Future runtime must atomically persist decision, invalidation and committed checkpoint; this architecture makes no persistence claim. |
| Overflow drops relevant changes | Fail closed, stop admission and fully invalidate potentially affected manifests; no sampling of invalidation truth. |
| Bursts create an unbounded fresh-read loop | Permit one pending requirement per frame-set generation and coalesce later causes without renewing authority. |
| Shared practice observer leaks active session context | Observer never receives manifest/session inventory; fanout is payload-free and each session lease independently rechecks scope and relevance. |
| Disable or recovery restores stale frames | Lifecycle is monotonic; disablement stops future admission but cannot return retired context to `CURRENT`. |
| Event directly invokes a fresh read | Temporal output is an inert requirement only; separate current human/session authority, new no-wider grant and source-specific authorization are mandatory. |
| Event becomes provider input or command evidence | Fixed false provider/command ceilings and explicit prohibition from context, audit and confirmation evidence. |
| Policy or principal rotates without new baseline | Rotation consumes observer generation, checkpoint eligibility and unclassified input; successor establishes a new verified baseline. |
| Architecture document is mislabeled live evidence | Strict architecture-only evidence label and static checks proving no runtime/API/database/listener/provider/command artifact. |
| Self-consistent substituted provenance crosses proofreading | Reconstruct policy, binding, observation, manifest/lease, decision and signal digest from authoritative inputs; never trust a supplied temporal envelope. |

## Residual risks deliberately deferred

Real PostgreSQL/outbox/feed implementation, authentication transport,
RLS/ABAC, transaction isolation, checkpoint durability, process ownership,
restart recovery, fanout load, backpressure sizing, retention, operational
audit, deployment and privacy assessment require separately frozen and
reviewed descendants.

## Forbidden openings

No patient, clinical, financial, product-derived, historical-PHI or protected
data; no raw audit; no live database/outbox/feed/watcher/listener/source reader;
no migration, trigger, route, GraphQL subscription, persistence, broker,
background worker or scheduler; no provider or external retrieval; no command
or write; no product runtime; no deployment, production, release, Pages,
protected evidence or protected-ref movement. Preserve and exclude
`docs/branding/` and unrelated untracked artifacts.
