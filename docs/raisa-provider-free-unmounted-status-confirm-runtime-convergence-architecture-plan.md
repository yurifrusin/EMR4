# Provider-free unmounted status-confirm runtime convergence architecture plan

Date: 2026-08-12

Source HEAD: `fca97097eeca5070ad41e403aed9413eee45ccba`

Status: `frozen_for_provider_free_unmounted_architecture`

## Purpose

Freeze the narrowest architecture that could converge the existing
status-confirm route on the accepted pure adapter and transaction protocol
without weakening its current response, audit or idempotency behavior. The
tranche closes architecture questions only. It does not edit/import or execute
an application route or database and cannot admit a runtime implementation.

## Exact accepted inputs

Only these non-protected artifacts may be read or content-searched:

| SHA-256 | File |
|---|---|
| `5f3ccdf0b95151ef2013530e23e317b3aafcfa3d177ebc119a8ffe9400875806` | `docs/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review-closeout.md` |
| `e9aac014b2111a5c48563b1cf5386b734d9d95948d0157262d2db8d6cb71292a` | `orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-contract.json` |
| `54acf1b0b04e2387d64b778debedeb857204408dd4e7f4ea4922101b4ff260e1` | `orchestration/continuity/raisa-provider-free-read-only-status-confirm-runtime-gap-admission-review/runtime-gap-review-evidence.json` |
| `297e34fbd984baeb53892edf5bc67f3d4db15911fa83d0b59776b2d707bffc30` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract/adapter-contract.json` |
| `89140cc9f46dfb01cac2bcb9d0531be06b81d02b7d9ce0d779e8b456148f4144` | `orchestration/continuity/raisa-provider-free-unmounted-status-confirm-kernel-adapter-contract/adapter-contract.schema.json` |
| `2967703f8baf395439a6e2c88885074fefe9f4bea308c0294ba7e67c57b26633` | `orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-packet.json` |
| `962a6fa2ee82226df2975a7f3c82d3f445498ef727b3d5addf4b891a380f840c` | `orchestration/continuity/raisa-provider-free-unmounted-status-transaction-kernel-protocol-rehearsal/protocol-packet.schema.json` |
| `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` | `orchestration/api_spine_adr.md` |
| `c3885ccee077df8f316b8ee8167d56a00673473841cbd57401df980d2a61c4b6` | `docs/api-spine/openapi/appointment-commands.yaml` |

No repository, application, `tests/`, `docs/` or orchestration-directory
content search is permitted. A need for another source stops the tranche and
requires an explicit plan revision.

## Frozen architecture decisions

1. **Status-only seam.** The existing confirmation-family route must
   discriminate `update_appointment_status` before constructing the kernel
   ingress. Waiting-area confirmation remains outside this kernel and unchanged.
2. **Server-owned ingress.** Practice, actor, role, active-user and opaque
   session-binding facts come only from backend authority/session services.
   Transport fields cannot assert or override them.
3. **Ordered transaction.** One backend-owned transaction acquires
   `practice -> appointment -> idempotency_record`. The unused schedule-domain
   lock is skipped, never reordered. No receipt/conflict is disclosed before
   all locks and the current-authority recheck.
4. **Durable current-state identity.** The locked appointment authority adapter
   must expose a monotonically increasing `appointment_state_version`. The
   signed confirmation binds that version plus practice, target, actor,
   session-binding digest, command, warnings and freshness. Physical column,
   migration and backfill design remain outside this tranche.
5. **Exact warnings.** After locked-state recomputation, submitted warning
   codes must equal the current canonical unique set. Missing, extra, duplicate
   or unknown codes stop effect-free.
6. **Terminal policy.** A terminal appointment requested to move to a different
   status stops as `transition_policy_deferred`. This architecture does not
   invent a new product transition policy.
7. **Atomic write set.** Only `committed` may stage an appointment mutation,
   attributable audit and completed receipt. The receipt durably binds target,
   audit, idempotency identity, request digest, pre/post state versions and
   canonical response digest. All three commit or roll back together.
8. **Authority-first idempotency.** Same-key replay and different-digest
   conflict classification occur only after current authority and target
   validity are rechecked inside the ordered transaction.
9. **Canonical delivery.** Initial success and replay render the exact stored
   canonical receipt bytes. Failure after commit is `delivery_unknown`; the
   server performs no second effect and a same-key retry returns the stored
   receipt.

## Authored-synthetic evidence

A provider-free architecture validator will:

- validate one closed contract and schema;
- verify all nine source hashes;
- check the nine decisions and exact cross-bindings;
- evaluate at least eighteen authored-synthetic architecture scenarios over
  discrimination, authority loss, lock order, warning/evidence/version drift,
  terminal deferral, replay/conflict timing, rollback and response loss;
- reject at least forty hostile contract/scenario mutations; and
- emit minimized evidence without importing application code or a database
  library.

## Acceptance

The tranche passes only if:

1. the fresh five-source receipt and all nine accepted-input hashes pass;
2. all architecture records are closed and `implementation_authorized` is
   exactly `false`;
3. every scenario follows the frozen trace and effect/disclosure rule;
4. at least eighteen scenarios and forty hostile mutations pass;
5. focused, dependency, API Spine, baton and whitespace gates pass;
6. the application tree remains unchanged; and
7. protected refs and all unrelated untracked files remain unchanged.

## Forbidden surfaces

No application edit/import, route or database execution, SQL, real lock,
physical schema/migration/backfill, source or watcher access, event transport,
provider call, credential/IAM/browser authorization, network, executable tool,
product/patient data, command expansion, deployment, production, release,
Pages or protected-ref movement. Preserve and never stage `docs/branding/` or
any unrelated untracked file. Use explicit-path staging only.

## Recovery and next candidate

One mechanical contract/schema/script/test correction is permitted if it does
not change the nine decisions or any forbidden boundary. A conceptual conflict
stops at `revision_required`.

On acceptance, the next candidate is
`provider_free_unmounted_status_confirm_runtime_convergence_rehearsal`: a pure
in-memory state-machine rehearsal of this exact architecture. It remains
provider-free and unmounted and grants no route or database implementation.
