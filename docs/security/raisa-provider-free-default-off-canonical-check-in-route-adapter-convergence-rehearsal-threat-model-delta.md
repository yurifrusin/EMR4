# Threat-model delta — default-off canonical check-in route-adapter convergence

Date: 2026-08-18

Timestamp: 2026-08-18T12:05:29+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `ad523968713e58f0b42c3a428556c968f61d6d3c`

## New seam

The existing default-off A5.1 FastAPI confirmation route will become a
transport and dependency-binding layer over the accepted canonical check-in
adapter. The public route, feature/practice gate and typed request/response
contract remain unchanged.

## Assets protected

- exact default-off and authored-synthetic-practice admission;
- authenticated and transaction-time Receptionist authority;
- one-use signed evidence and stable idempotency precedence;
- locked appointment and compatible waiting-area truth;
- atomic status, audit, committed event, receipt and readback composition;
- the patient-free public response contract; and
- sealed evidence, protected refs and unrelated untracked files.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Importing the adapter silently opens A5.1 | Keep `_a5_check_in_gate_open` first; keep both existing settings unchanged and default-off; test zero adapter/dependency calls on denial. |
| Route retains a hidden second write path | One adapter call in the handler; forbid direct claim, lock, mutation, audit, event, completion and commit in the handler; no fallback on adapter stop. |
| Invalid changed body bypasses existing idempotency conflict semantics | Classify replay/conflict/in-progress through the dedicated claim before closed-envelope validation; roll back a newly started invalid envelope. |
| Adapter callbacks widen tenant or role authority | Server-supplied practice and actor only; exact-practice locked appointment, exact-practice active Receptionist reload and exact-practice waiting-area lookup. |
| Callback binder recomputes command meaning | Treat the accepted typed effect/audit/event plans as authoritative inputs and translate only into existing service calls. |
| Missing/cross-practice target leaks existence | Preserve the existing closed 404 mapping without target detail. |
| Adapter stop changes established HTTP semantics | Transport-only exhaustive reason mapping preserves the existing 200 blocked, 404, 409 and 503 families; unknown/internal/uncertain outcomes never become success. |
| Commit or readback uncertainty releases a false success | The adapter returns no successful receipt for commit/readback failure; the route raises the existing server-error posture and has no recovery write. |
| Waiting-area assignment becomes movement/removal | Accepted adapter permits only compatible assignment into empty state or preservation; move/removal reason codes remain blocked. |
| Event or receipt leaks patient/secret material | Existing patient-free schema plus accepted adapter allowlist; raw evidence/idempotency key never enters effect, audit, event or response. |
| GraphQL/event becomes command authority | REST remains the only command; event is written after accepted composition as a committed acceleration hint and cannot authorize another effect. |
| Tests accidentally exercise product or provider systems | Use static inspection, injected fakes and the existing repository-authored synthetic test fixture only; no product connection, external service or provider call. |

## Residual risk and claim boundary

This tranche does not prove production PostgreSQL/RLS, restart, crash or
unknown-commit recovery, ordinary-practice admission, first-party client
behavior, external adapter conformance, deployment or production. The A5.1
feature remains default-off and empty-allowlist denied outside explicit local
authored-synthetic configuration.

No generic-status `Arrived`, grammar, client, waiting-area move/removal,
product/patient/clinical/protected evidence, provider, live external network,
deployment, release, Pages or protected-ref action is in scope.
