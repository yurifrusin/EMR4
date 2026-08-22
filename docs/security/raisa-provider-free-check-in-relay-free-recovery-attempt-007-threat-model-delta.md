# Threat-model delta — check-in relay-free recovery attempt 007

Date: 2026-08-23

Timestamp: 2026-08-23T03:08:47.1921091+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-rollback-unknown-commit-recovery-attempt-007`

## Delta

Attempt 007 adds one collision-free, one-run disposable PostgreSQL namespace
against the accepted repaired Docker start/attach vector. It changes no base
harness, API Spine contract, product source, provider surface or protected ref.

| Threat | Fail-closed control |
|---|---|
| Reusing consumed negative evidence as execution authority | Bind the immutable attempt-006 terminal and accepted repair separately; neither authorises execution until the attempt-007 checkpoint publishes. |
| Reintroducing the unsupported start option | Byte-bind the repaired harness and repair attestation; statically require exactly `start --attach --interactive <container_id>`. |
| Short or invented Git identifiers | Require full 40-character commit objects, machine resolution and ancestor checks; prohibit Git IDs in caller-authored receipt prose. |
| Terminal collision, overwrite or retry | Closed attempt-007 namespace, pre-existing-terminal denial, one occupied count, zero retry, no delete/rotate/rename/overwrite. |
| Leaking credentials or raw attachment output | Random controller-memory credentials through inspected attached stdin only; closed sanitised terminal schema and no retained stdout/stderr. |
| Relay, port or external-network escape | One captured internal network; no published port, host relay, Docker-exec bridge, external network, bind, volume, multiprocessing process or queue. |
| False success after response loss | No caller success from the incomplete response; exact OCI/observer classification and fresh restricted authoritative readback alone decide commit state. |
| Partial, duplicate or cross-practice release | Forced RLS, non-owner `NOBYPASSRLS` role, exact packet membership, idempotency identity and zero other-practice visibility. |
| Cleanup uncertainty | One controller, captured-identity reinspection, unconditional teardown, exact absence proof; uncertainty is terminal failure with no retry. |
| Parallel custody split | Sol retains the indivisible lifecycle and cleanup lease; DeepSeek, Gemini and native subagents own no work package. |
| Product or authority creep | Default-off check-in, ordinary admission, generic-status `Arrived`, routes, clients, waiting area, product data, production, deployment, Pages and protected refs remain closed. |

## Residual claim limit

A pass proves only one authored-synthetic provider-free disposable PostgreSQL
rollback and unknown-terminal-response recovery under the frozen harness and
containment envelope. A failed run proves only its exact sanitised coordinate
and cleanup. Neither result grants model-provider, product, ordinary-practice,
real-data, reusable-runtime, production, deployment, release, Pages or
protected-ref authority.
