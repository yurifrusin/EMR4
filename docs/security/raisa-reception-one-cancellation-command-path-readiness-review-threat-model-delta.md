# Reception One cancellation command-path readiness review threat-model delta

Date: 2026-08-15

Timestamp: 2026-08-15T11:19:48+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: Yuri's 2026-08-15 selection of the cancellation direction
and the accepted post-combined-editor orientation at source
`2ca3a111d2ee9277571ea3c905f22ce78c8e9745`

## Changed surface

No runtime surface changes. This delta governs a repository-static review of
the currently mounted appointment cancellation routes and client behavior.

## Threats and required controls

| Threat | Required control |
|---|---|
| A destructive control is exposed because a route already exists | Require the complete proposal-confirm conditional-command pattern before any Reception One composition. Mounted code is not sufficient authority or readiness evidence. |
| A client falls back from delete semantics to status semantics without preserving meaning | Inventory the 404 fallback, cancellation text, reason code, audit action, idempotency derivation and confirm endpoint; select one product meaning before reuse. |
| Explicit confirmation is inferred from proposal metadata or a first click | Require a distinct affirmative human act and `confirmed=true` at the confirm boundary; no model, channel or delegate may self-confirm. |
| Signed evidence is valid but current truth changes before commit | Require a locked current appointment read and revalidation inside the mutation transaction, not only a pre-lock freshness comparison. |
| Actor authority is checked only when request dependencies resolve | Require current actor authority to be checked inside the same mutation transaction that commits cancellation. |
| Cancellation text or reason code is dropped | Bind both fields into proposal evidence and preserve them through confirmation, appointment truth and audit, subject to an explicit optional/required product policy. |
| Replay, response loss or duplicate clicks repeat the destructive effect | Require one operation-scoped idempotency record, exact request binding, atomic completion and exact replay semantics. |
| Raw compatibility delete is mistaken for preferred product authority | Keep it mounted and visible under the existing compatibility posture; do not route new Reception One behavior through it. |
| OpenAPI draft shape is mistaken for exact runtime truth | Record path and schema differences; do not claim conformance or silently modify either surface. |
| Fresh UI reload is treated as transactional correctness | Preserve fresh readback for user reconciliation, while enforcing truth, authority, idempotency and audit within the backend commit boundary. |
| Read-only findings are overstated as runtime proof | Label evidence repository-static and prove no concurrency, product, patient, database or production behavior. |

## Residual boundary

This review can select a narrow architecture prerequisite. It cannot expose a
cancellation control, change route behavior, prove concurrent database safety
or settle optional-versus-required cancellation-text product policy beyond the
current reason-code behavior. Those require separately frozen descendants.
