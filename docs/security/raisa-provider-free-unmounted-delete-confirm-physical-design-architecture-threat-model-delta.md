# Threat-model delta — delete-confirm physical-design architecture

Date: 2026-08-15

Timestamp: 2026-08-15T15:24:20+10:00 (Australia/Brisbane)

Source HEAD: `6514d35c465e304a421218890264f61c33ba51bb`

Status: `frozen_for_provider_free_unmounted_architecture`

## Scope

This delta covers only the selected, unmounted additive authority-generation,
capability-grant, delete-audit, private-receipt and ordered-transaction design.
It is architecture-only and processes no product, patient or clinical data.

## Threats and controls

| Threat | Frozen control |
|---|---|
| Authored-synthetic application-auth state is mistaken for product authority | Use the product `users` row and closed product capability relation; synthetic relations remain ineligible. |
| A route role grants cancellation | Require active exact membership, an admitted role, current signed generation and exact `appointment.cancel.confirm` while the fence is locked. |
| A model, client or channel invents authority | Server selects practice/actor/session; grants are database rows and signed generation is verified against locked truth. |
| Capability wildcard expands authority | Capability vocabulary is closed to exact strings; row absence denies and no wildcard is representable. |
| Existing users receive authority during migration | Capability table is created empty; no automatic or role-derived grant is permitted. |
| Revocation races a command | Every grant/user authority change advances the parent generation and conflicts with the held parent `FOR SHARE` lock. |
| Authority is revoked and later restored under the same identity | Monotonic generation changes; an old proposal/receipt binding cannot pass as the new generation. |
| Direct SQL chooses or suppresses generation | Database triggers override submitted generations, advance exact authority changes once and fail on overflow. |
| Practice or actor substitution | Composite user and grant identity plus server-owned practice/actor binding are checked twice in-transaction. |
| Target enumeration leaks through idempotency | Appointment absence and first authority failure stop before idempotency access or disclosure. |
| A legacy row is replayed as a complete receipt | Only a family-qualified complete v1 receipt is replayable; null-version legacy rows fail closed. |
| Same key is reused for a different command | Exact actor/role/generation/session/operation/route/target/request binding returns non-disclosing conflict. |
| Stored JSON is reserialized into a different outcome | Canonical bytes are delivery authority; initial response and replay use the same buffer. |
| Stored receipt bytes are corrupted | Recompute SHA-256 and compare in constant time before any replay disclosure. |
| Raw authenticated session identity becomes durable | Store only a domain-separated 32-byte HMAC digest and bind audit through the private command row. |
| Cancellation reason is absent or silently weakened | Dedicated ingress requires the exact current `Cancelled` code set and preserves nullable text independently. |
| `LEGACY_UNCLASSIFIED` becomes a dedicated reason | Reject it explicitly; compatibility history gains no dedicated authority. |
| Human warning acknowledgements and internal evidence are conflated | Store them in separate bounded audit fields; legacy merged arrays are not reinterpreted. |
| Audit cannot prove the waiting-area or version transition | Versioned audit v1 records pre/post version and waiting-area values and is atomically linked to the receipt. |
| Full appointment data leaks in a command receipt | Six-field patient-free canonical response excludes the full appointment read model and internal audit/session fields. |
| Concurrent keys cause two effects | Lock authority fence, appointment and idempotency row in one global order and commit mutation/audit/receipt together. |
| Concurrent insert bypasses idempotency locking | Insert target-bound row with conflict-do-nothing, then lock the unique winner without releasing earlier locks. |
| Lock waits hang or reset per acquisition | Enforce one cumulative 2000 ms deadline and apply only its remaining positive budget. |
| `NOWAIT`, skip-locked or retries create ambiguous outcomes | Forbid `NOWAIT`, `SKIP LOCKED`, advisory locks and hidden effect retries. |
| Connection loss creates duplicate cancellation | Pre-commit loss rolls back; post-commit unknown delivery recovers only through same-key exact receipt replay. |
| Readback is treated as commit proof | Commit receipt is authoritative outcome; separately authorised fresh readback is reconciliation only. |
| Cancellation capability implies display access | Require the separate exact `appointment.read` grant after commit. |
| Raw delete or status fallback enters the new kernel | Admit only dedicated delete-confirm operation/route; compatibility families remain separate. |
| Event, Context Fabric or provider output becomes command authority | They remain inert proposal/cue inputs and cannot create grants, confirmations, locks or writes. |
| Architecture evidence executes product code | Validator imports no application, migration, database, network or provider module. |
| A future downgrade erases used authority or receipt meaning | Rollback is schema-only before first use; after use recovery is forward-only and fail-closed. |

## Residual risks

- The design does not prove PostgreSQL DDL, trigger behavior, RLS, lock timing,
  deadlock handling, driver behavior, migration cost or transaction execution.
- No production identity provisioning or capability administration workflow is
  designed or authorised here.
- The exact API compatibility/version transition away from the current full
  delete-confirm response remains a later gate.
- No UI, channel adapter, patient delegation, event or provider behavior is
  exercised.
- Operational recovery after first deployed use, observability, retention and
  performance remain separately gated.

## Authority boundary

No application/model/migration/service/route edit or import, executable DDL,
database connection, real lock, capability grant, provider call, product or
patient data, command, deployment, production, release, Pages or protected-ref
movement is authorised. `implementation_authorized` remains false.
