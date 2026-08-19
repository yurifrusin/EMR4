# Threat-model delta: check-in relay-free recovery attempt 003

Date: 2026-08-19

Timestamp: 2026-08-19T23:20:30.4199339+10:00 (Australia/Brisbane)

Status: `frozen`

This delta authorises one separately named provider-free disposable
PostgreSQL attempt after the accepted no-credential Created-state correction.
It grants no product or ordinary-practice authority.

## Assets and trust boundaries

- Immutable attempt-001 and attempt-002 failure, cleanup and envelope evidence.
- Immutable Created-state representation evidence and repair attestation.
- Full 40-character plan, correction, transport and runtime-role Git bindings.
- One fixed attempt-003 output namespace and one terminal envelope.
- One internal Docker network, server and fixed-action sidecars.
- In-memory ephemeral credentials delivered only after exact inspection.
- Admin-owned forced-RLS probe relations and a non-owner `NOBYPASSRLS` role.
- Exact terminal OCI state, authoritative readback and sanitized evidence.

Trust crosses only the host Docker API, post-inspection attached stdin, the
captured internal network, PostgreSQL authentication/RLS and closed validators.
Attachment output, Docker logs, model prose and process timing are not outcome
evidence.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A new attempt overwrites or launders predecessor failures | Attempt 003 has a distinct operation and exact output directory; attempt-001 and attempt-002 artifacts are hash-bound and immutable. |
| The Created-state correction silently broadens containment | The exact representation evidence, repair attestation, correction source and corrected harness digest are bound; only empty-before-attachment or captured-ID-after-attachment endpoint states are admitted. |
| A path argument redirects evidence or overwrites unrelated files | Output topics are a closed code allowlist; the wrapper exposes no path argument and refuses any pre-existing terminal file. |
| More than one occupied execution occurs | The plan and latch admit exactly one wrapper invocation; terminal collision prevents a second run; no retry path exists. |
| A pre-return lifecycle error strands a Created object | Every captured acquisition is owned by one controller and is exactly cleaned before the primary error propagates. |
| Host transport ambiguity returns | No listener, published port, relay, `docker exec` byte bridge, multiprocessing process or queue is allowed. |
| Attachment status is mistaken for transaction outcome | Attachment output/status is discarded; exact OCI state, observer evidence and restricted authoritative readback are required. |
| Credential or nonce reaches an unauthorised surface | Actual credential values must be absent from Docker configuration; the nonce must exist at exactly one ownership label and nowhere else; evidence redaction scans both. |
| Rollback leaves a partial packet | Fresh restricted readback must observe zero effect, receipt and audit members. |
| Ambiguous response is retried or released as success | Retry count and success release are structurally zero; only authoritative readback may classify committed-exactly-once. |
| Cross-practice inference or role escalation occurs | Enabled and forced RLS, transaction-local practice scope, non-owner `NOBYPASSRLS`, closed grants and other-practice zero visibility. |
| Partial or contradictory committed state is accepted | Exact packet cardinality, identities, request digest, action/outcome and cross-references are required; all other shapes deny. |
| Evidence omits the new authority boundary | The attempt envelope binds the resolved plan commit, correction source and evidence, exact run source, one execution, terminal digest, zero retry and cleanup. |
| Cleanup touches unrelated objects or leaves residue | One owner acts only on captured IDs after nonce/name/label/image/network reinspection; matching owned resources must be zero. |
| Rehearsal is mistaken for ordinary or production admission | Provider-free/authored-synthetic/disposable labels and zero ordinary/product effects are mandatory; no configuration or route changes occur. |

## Residual limits

The attempt proves one serial authored-synthetic explicit rollback and
caller-level incomplete-terminal-response recovery on the admitted local
Docker/PostgreSQL configuration. It does not prove an in-WAL crash,
distributed partition, driver/pool behavior, concurrency, product-schema
compatibility, ordinary-practice safety or production availability.

## Closed boundaries

No live/existing/cloud/product database, provider call before successful local
admission, external network, product/patient/appointment/clinical/protected
data, ordinary-practice enablement, feature-flag or allowlist change,
canonical route change, generic-status `Arrived`, action grammar, first-party
client, waiting-area movement, REST/OpenAPI, GraphQL, async contract,
deployment, release, Pages, protected evidence access or protected-ref
movement is authorised.
