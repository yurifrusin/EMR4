# Threat-model delta: Docker Created-state profile conformance repair

Date: 2026-08-19

Timestamp: 2026-08-19T22:26:59.3728655+10:00 (Australia/Brisbane)

Status: `frozen`

Parent controls are the accepted relay-free OCI-result transport, restricted
runtime-role/forced-RLS floor and immutable attempt-002 failure/cleanup
evidence. This delta permits one never-started Docker representation reading
and two evidence-proven predicate corrections only.

## Assets and trust boundaries

- Full 40-character Git and SHA-256 causal bindings.
- Exact Docker Engine 29.5.3 and cached PostgreSQL 16 image identity.
- One captured internal network and one captured never-started container.
- Cryptographic ownership nonce and controller-only non-credential canaries.
- Sanitized closed representation evidence and post-correction attestation.
- Immutable attempt-002 envelope, failure, execution count and old harness
  digest.

Trust crosses only the host-to-Docker control API for create, inspect and
captured-ID cleanup. No container process, stdin attachment, database,
credential, external network or provider boundary is crossed.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A representation probe accidentally becomes a database attempt | Source and command admission forbid Docker start/attach/exec, stdin, credentials, PostgreSQL, SQL and transaction code; the container must remain `created` and `Running=false`. |
| A wrong Docker object is inspected or removed | Capture IDs from create, require exact name/image/labels/nonce before every action, remove by captured ID only and independently count the conformance label. |
| Raw inspect data leaks identities, paths or secret-shaped values | Retain only booleans, counts and closed relation enums; closed schemas deny raw keys, object identities, nonce, canaries, argv, env and paths. |
| The ownership nonce is mistaken for a credential | Credential canaries/values are scanned separately; nonce is required at one exact label and a defensive-copy scan requires absence outside that label. |
| Credential scanning is weakened while fixing the contradiction | Full `Config`/`HostConfig` continues to be scanned for actual credential values; the broader evidence redaction scan still includes credentials and nonce. |
| Empty Created-state endpoint identity admits an unrelated network | Require one exact network-map key equal to the captured name plus exact `HostConfig.NetworkMode`; endpoint identity may only be empty before start or the captured ID after attachment. |
| A permissive network fallback enters the repair | No substring, prefix, truthy, multi-network, unknown-key, foreign-ID or arbitrary network-mode acceptance is allowed. |
| Failure residue contaminates a later attempt | `finally` cleanup, primary-error preservation, captured-ID absence and independent zero-label readback are mandatory; failure consumes the one run. |
| Historical failure evidence is silently rebound to repaired code | The old harness digest is resolved from its exact full Git source; current repaired bytes have a distinct attested digest; the attempt-002 envelope is never edited. |
| The consumed attempt is accidentally rerun | Its terminal namespace remains occupied and its wrapper's empty-namespace gate remains mandatory. |
| Rehearsal evidence is overstated | Claim is limited to Docker 29.5.3 Created-state representation and two containment predicates; no database, credential, transaction, runtime or product claim follows. |

## Residual limits

The proof does not establish Docker behavior on another engine version,
container start/reattachment, PostgreSQL readiness, credential delivery,
transaction rollback, unknown-response recovery, crash recovery, concurrency,
production cleanup or product compatibility. A later database attempt needs a
separate frozen plan and exact one-run envelope.

## Closed boundaries

No live/existing/cloud/product or disposable database, provider call, external
network, product/patient/appointment/clinical/historical/protected data,
ordinary-practice enablement, feature flag, allowlist, route mounting,
generic-status `Arrived`, action grammar, first-party client, waiting-area
movement, product/API/schema/configuration source, deployment, release, Pages,
protected evidence access or protected-ref movement is authorised.
