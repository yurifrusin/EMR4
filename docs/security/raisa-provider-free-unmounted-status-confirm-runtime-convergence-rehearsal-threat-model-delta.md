# Threat-model delta — unmounted status-confirm convergence rehearsal

Date: 2026-08-12

Source HEAD: `0fe6b9bfaea2394d7fb7ebb9866bfb1fa56611cc`

## Scope

This delta covers one provider-free, pure in-memory state-machine rehearsal of
the accepted status-confirm convergence architecture. It uses authored-
synthetic data only. `implementation_authorized: false` is invariant.

## Threats and controls

| Threat | Deterministic control |
|---|---|
| Waiting-area input reaches the kernel | Discriminate before any modeled lock or state access. |
| Transport invents authority/session | Require complete server-owned ingress and an opaque exact session binding. |
| Lock order drifts | Freeze and record `practice -> appointment -> idempotency_record` for every eligible invocation. |
| Revoked authority learns a stored outcome | Recheck current authority before idempotency inspection or disclosure. |
| Removed target leaks a replay | Require current target existence under the appointment-lock step before idempotency inspection. |
| Stale version or warning acknowledgement mutates | Compare locked version and exact unique warning sets before signed evidence and effect. |
| Terminal product policy is invented | Emit effect-free `transition_policy_deferred`. |
| Partial mutation survives failure | Stage mutation/audit/receipt in a private copy and publish only the complete atomic copy. |
| Concurrent same-key request repeats the effect | First participant stores one receipt; the second returns identical stored bytes with zero new write. |
| Different-digest reuse leaks or mutates | Return conflict after authority/target checks with no new write or receipt disclosure. |
| Lost response causes server retry | Preserve `delivery_unknown`; only a same-key client retry may read the stored receipt after fresh checks. |
| Simulator is mistaken for runtime proof | Keep database/application imports absent and every forbidden effect false. |
| Evidence scope expands | Verify only eight exact accepted inputs; AER-0291 forbids broader content search. |

## Residual risks

The rehearsal cannot prove physical state-version representation, migration or
backfill; ORM/service composition; PostgreSQL locking, isolation, rollback or
race behavior; mounted-route parity; restart/unknown-commit recovery;
waiting-area regression behavior; or operational safety.

## Authority boundary

No real route, database, source, lock, provider, credential, browser, product
or patient data, watcher, event, command, deployment, production, release,
Pages or protected ref is opened. `docs/branding/` and unrelated untracked paths
remain excluded.
