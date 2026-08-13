# Threat-model delta — disposable PostgreSQL status-confirm product-adapter integration

Date: 2026-08-13

Timestamp: 2026-08-13T11:03:40+10:00 (Australia/Brisbane)

## New evidence seam

One unmounted product adapter will run against one owned disposable PostgreSQL
16 server containing only fixed authored-synthetic administrative rows. The
tranche composes previously separate adapter and physical proofs; it creates no
route or reusable runtime.

## Threats and controls

| Threat | Required control |
|---|---|
| Fresh session reaches RLS tables before tenant context | Establish transaction-local `app.current_practice_id` in the physical seam's exact-practice callback before the appointment lock; restore it again before both user reads. |
| Tenant setting leaks through the connection pool | `set_config(..., true)` only inside the physical transaction; prove the setting absent outside commit and rollback transactions. |
| Practice context is client-selected | Use only the authenticated server user's exact practice; HMAC proposal and version bindings remain mandatory. |
| Stale or disabled actor wins during lock wait | Query the actual user row twice with `populate_existing`; exact active/practice/role match on both checks. |
| Cross-practice row is disclosed | Forced RLS on all practice-scoped adapter tables plus exact zero-visibility probes under a different tenant setting. |
| Projection failure leaves a partial write | Let the existing composition and physical final guard roll back appointment, audit, receipt and trigger-owned version together. |
| Retry repeats the effect | Reconstruct the stable proposal-time request, classify the completed idempotency row first and release only validated stored canonical bytes. |
| Text/UUID representation drift turns an exact retry into a conflict | Preserve canonical signed request bytes, but normalize the already-admitted target to UUID in the adapter's physical-factory wrapper before the ORM comparison. |
| Disposable server reaches external networks or persists data | Cached image, internal network, no published port, fixed loopback relay, tmpfs, no mounts, bounded resources and exact-ID cleanup. |
| Harness records secrets or synthetic row bodies | Closed evidence schema admits only digests, fixed labels, counts, versions and value-free tokens. |
| Cleanup removes an unrelated object | Captured exact IDs plus name/image/nonce/label/network/tmpfs/resource reinspection; ambiguity stops. |

## Residual boundary

Serial disposable behavior does not prove concurrent authority changes,
restart, unknown commit, long-lived pool hygiene, product migration-chain
operation, HTTP transport or UI behavior. Those remain separately gated. No
product data, route, provider, credential, deployment or protected-ref
authority is opened.
