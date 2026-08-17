# Threat-model delta — canonical check-in product-adapter extraction rehearsal

Date: 2026-08-18

Timestamp: 2026-08-18T08:58:42+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `852f6f26089cf081c205aff952dffcdecb80d63b`

## Assets protected

- one future canonical ordinary-arrival command meaning;
- exact current human authority and locked appointment truth;
- one-use opaque evidence and stable idempotent replay;
- waiting-area assignment/preservation integrity;
- atomic status, audit, committed event, receipt and readback composition;
- the default-off A5.1 admission boundary; and
- protected refs, sealed evidence and all unrelated untracked files.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| The reusable adapter silently enables A5.1 | Adapter reads no settings and contains no feature/practice allowlist; the unchanged route retains the only A5.1 gate. |
| A stale client role or proposal authorizes the write | Require an injected current active same-practice Receptionist inside the command session; client assertions and proposal provenance confer no authority. |
| Bare `Arrived` assignment substitutes for check-in | Admit only the dedicated check-in schema and exact `Booked|Confirmed -> Arrived` contract with one-use evidence and dedicated event/receipt meaning. |
| Replay creates a second effect | Classify stored same-key replay before lock/effect and require zero later callbacks; conflict, in-progress and different-key evidence reuse fail closed. |
| Stale/tampered evidence survives | Recompute exact current state, target area and freshness and verify the opaque evidence against current actor/practice/appointment/status/area/time. |
| Waiting-area move, removal or cross-tenant assignment leaks in | Exact-id, active, same-practice, same-location validation; supplied area assigns only into an empty slot and omission/null only preserves. |
| Partial effect is labelled successful | Ordered injected callbacks, rollback on pre-commit failure, bounded receipt only after complete/commit/readback, and no generic success fallback. |
| Patient or secret material leaks through event/receipt | Exact patient-free allowlists; reject raw evidence, idempotency keys, patient identifiers, names, notes or clinical text in released structures. |
| The rehearsal becomes a live command | No router/config/SessionLocal/server/database import; injected authored-synthetic fakes only; route remains hash-exact and has no adapter import. |
| An event becomes authority or source truth | Event is emitted only after accepted effect composition and remains a committed acceleration hint; command-time truth and readback are separate. |
| Two canonical arrival paths are created prematurely | Generic status, action grammar and both clients remain unchanged; later atomic convergence remains a separate tranche. |

## Residual risk and claim boundary

The adapter is not yet carried by HTTP and does not prove real transaction,
RLS, concurrency, restart or response-loss behavior. The current mounted A5.1
path continues to own its existing default-off development behavior until a
later route-convergence tranche explicitly wires the adapter. Generic status
still carries current first-party `Arrived` behavior until the later atomic
two-client cutover.

No product data, patient/clinical/protected evidence, provider, live database,
network, deployment, production, release, Pages or protected-ref action is in
scope.
