# Threat-model delta: check-in relay-free recovery attempt 002

Date: 2026-08-19

Timestamp: 2026-08-19T21:47:53+10:00 (Australia/Brisbane)

Status: `frozen`

This delta authorises one separately named provider-free disposable
PostgreSQL attempt after Yuri's explicit confirmation. It grants no product or
ordinary-practice authority.

## Assets and trust boundaries

- Immutable attempt-001 failure and cleanup artifacts.
- Full 40-character plan, repair, transport and runtime-role Git bindings.
- One fixed attempt-002 output namespace and one terminal envelope.
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
| A restart overwrites or launders attempt-001 failure | Attempt 002 has a distinct operation and exact output directory; predecessor artifacts are hash-bound and immutable. |
| A path argument redirects evidence or overwrites unrelated files | Output topics are a closed code allowlist; the wrapper exposes no path argument and refuses any pre-existing terminal file. |
| More than one occupied execution occurs | The plan and latch admit exactly one wrapper invocation; terminal collision prevents a second run; no retry path exists. |
| The pre-return lifecycle defect recurs and strands a Created object | Repair source `fc772085a02d7db790b938fb845ef4546156d31e` self-cleans exact captured acquisitions before propagating the primary error. |
| Host transport ambiguity returns | No listener, published port, relay, `docker exec` byte bridge, multiprocessing process or queue is allowed. |
| Attachment status is mistaken for transaction outcome | Attachment output/status is discarded; exact OCI state, observer evidence and restricted authoritative readback are required. |
| Credential reaches Docker configuration, files, logs or artifacts | Create then inspect; deliver one bounded line over captured-ID stdin; logging is disabled; recursive redaction and exact cleanup apply. |
| Rollback leaves a partial packet | Fresh restricted readback must observe zero effect, receipt and audit members. |
| Ambiguous response is retried or released as success | Retry count and success release are structurally zero; only authoritative readback may classify committed-exactly-once. |
| Cross-practice inference or role escalation occurs | Enabled and forced RLS, transaction-local practice scope, non-owner `NOBYPASSRLS`, closed grants and other-practice zero visibility. |
| Partial or contradictory committed state is accepted | Exact packet cardinality, identities, request digest, action/outcome and cross-references are required; all other shapes deny. |
| Evidence omits the new authority boundary | The attempt envelope binds the resolved plan commit, repair source, exact run source, one execution, terminal digest, zero retry and cleanup. |
| Cleanup touches unrelated objects or leaves residue | One owner acts only on captured IDs after nonce/name/label/image/network reinspection; matching owned resources must be zero. |
| Rehearsal is mistaken for ordinary or production admission | Provider-free/authored-synthetic/disposable labels and zero ordinary/product effects are mandatory; no configuration or route changes occur. |

## Residual limits

The attempt proves one serial authored-synthetic explicit rollback and
caller-level incomplete-terminal-response recovery. It does not prove an
in-WAL crash, distributed partition, driver/pool behavior, concurrency,
product-schema compatibility, ordinary-practice safety or production
availability.

## Closed boundaries

No live/existing/cloud/product database, provider call, external network,
product/patient/appointment/clinical/protected data, ordinary-practice
enablement, feature-flag or allowlist change, canonical route change,
generic-status `Arrived`, action grammar, first-party client, waiting-area
movement, REST/OpenAPI, GraphQL, async contract, deployment, release, Pages,
protected evidence access or protected-ref movement is authorised.
