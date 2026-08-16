# Threat-model delta — delete-confirm response compatibility and product-adapter architecture

Date: 2026-08-16

Timestamp: 2026-08-16T16:33:54.6870685+10:00 (Australia/Brisbane)

Status: `frozen`

Parent controls: accepted delete-confirm conditional-command kernel,
physical design/scaffold/serial behavior, read-only route-convergence review,
API Spine command ownership and active Ariadne controls.

| ID | Threat | Required control |
|---|---|---|
| `DPA-001` | A client supplies role, authority generation, capability or session identity. | Derive every authority field from authenticated server state; minimize the bearer token; physical seam owns the constant capability and two current checks. |
| `DPA-002` | Valid signed evidence is replayed against a later appointment generation. | Opaque evidence-signature/source-version HMAC plus locked current-version re-admission. |
| `DPA-003` | Unlocked status, waiting-area or reason state becomes effect authority. | Rebuild the exact delete state from the physical seam's locked appointment and repeat admission before staging. |
| `DPA-004` | Route-local claim, audit or mutation bypasses the accepted transaction seam. | Only `delete_confirm_locked_transaction`; no route fallback or second implementation. |
| `DPA-005` | The six-field private receipt is relabelled as `AppointmentOut`. | A distinct versioned minimal public envelope with a receipt field; success contains no appointment projection. |
| `DPA-006` | Exact replay is obtained by persisting full patient/practitioner/notes/schedule data. | Persist only the accepted six fields and project the full public envelope purely from those validated bytes. |
| `DPA-007` | Replay reconstructs a different body from later mutable database truth. | Initial and replay delivery use the same versioned pure canonical projection and perform no current appointment read for response construction. |
| `DPA-008` | Code/version drift changes replay bytes. | Immutable v1 projection constants, explicit schema versions, canonical sorted-key JSON and hostile mutation tests. |
| `DPA-009` | Unknown or reordered warning codes produce uncontrolled messages. | Exact one-entry warning registry; unique sorted stored codes; unknown/duplicate/order mismatch denies. |
| `DPA-010` | A cross-practice or unavailable target is distinguished through error detail. | One non-disclosing target-unavailable mapping and no partial/current body. |
| `DPA-011` | A legacy/in-progress/corrupt receipt leaks partial success or triggers an effect retry. | Closed 409/503 mappings; no body from partial state and no effect retry. |
| `DPA-012` | Raw DELETE inherits dedicated idempotency/capability semantics. | Explicit import/call/contract isolation; separate legacy governance only. |
| `DPA-013` | Canonical and compatibility aliases produce different success schemas. | One future handler and exact public-envelope version on both aliases; no dual response mode. |
| `DPA-014` | Architecture evidence opens product/runtime authority by implication. | Provider-free exact-source validation only; explicit no-route/no-database/no-product claim boundary. |

## Residual boundary

The architecture does not prove that the current schema, client or route can
consume the v1 minimal receipt envelope. Those changes require later separately
frozen unmounted implementation and route convergence. It also does not prove
database behavior beyond the accepted serial physical evidence, concurrency,
restart, unknown-commit recovery, deployment or production.

No patient/clinical/product data, protected evidence, provider/credential,
route/database execution, capability provisioning, deployment, release,
Pages or protected-ref authority is introduced.
