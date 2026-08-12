# Threat-model delta: unmounted status transaction-kernel protocol

Date: 2026-08-12

Parent: `docs/security/raisa-provider-free-compatibility-conformance-harness-temporal-idempotency-readiness-repair-threat-model-delta.md`

Status: `frozen_unmounted_delta`

| Threat | Fail-closed control |
|---|---|
| Receipt disclosure after authority revocation | Current authority is rechecked after ordered lock acquisition and before idempotency inspection. |
| Duplicate status write after lost response | Mutation, audit and receipt commit together; same-digest retry returns the original receipt without another effect. |
| Partial durable effect | Every pre-commit injection rolls back appointment, audit and receipt state together. |
| Mixed lock-order deadlock | Status admits only `practice -> appointment -> idempotency_record`; schedule-domain is skipped, never reordered. |
| Stale confirmation wins after waiting | Expected appointment version is rechecked under the ordered locks. |
| Idempotency identity confused with confirmation | Confirmation and idempotency are separate inputs and separate precedence phases. |
| Terminal re-transition policy smuggled into runtime | The scenario is explicitly deferred and effect-free; no product behavior changes. |
| Existing ledger-first helper mistaken for conformance | The design records it as a later reconciliation gap and imports no application helper. |
| Synthetic rehearsal mistaken for persistence proof | Locks, writes, rollback and commit are in-memory trace semantics only. |
| Scope broadens through imports or I/O | Deterministic tests reject application/database/network/provider imports and all effect-boundary flags remain zero. |
| User-owned material is staged | Explicit-path staging excludes `docs/branding/` and every unrelated untracked file. |

The packet contains only `syn-` identifiers, fixed non-secret digests, status
labels, versions and trace steps. It contains no person, patient, clinical,
product-derived or provider data.
