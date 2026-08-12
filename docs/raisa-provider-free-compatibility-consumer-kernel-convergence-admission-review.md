# Compatibility-consumer and kernel-convergence admission review

Date: 2026-08-12

Status: `frozen_read_only_finding`

## Finding

Repository evidence no longer supports the idea that the native product needs
the raw appointment writes. It does support keeping them mounted: repository
inspection cannot identify external consumers, and the remaining conformance
suite deliberately exercises current raw behavior.

| Consumer class | Result | Consequence |
|---|---|---|
| Native Diary/product runtime | zero raw mutation calls | ordinary product behavior is no longer a retirement blocker |
| Other committed runtime/application code | zero raw HTTP callers | no second in-repository product caller was found |
| Import/recovery/migration/operational scripts | zero raw HTTP callers | no committed system route consumer needs migration today |
| Tests and review probes | 126 direct call expressions in 21 files | preserve or deliberately migrate witnessed behavior |
| Direct database fixtures/bootstrap | four named tools | separate non-route obligation; never evidence of route or command authority |
| External consumers | unknown | routes stay mounted; no retirement or signal-mode conclusion |

## Conformance baseline health

The remaining tests are useful but not uniformly current. The broad ordinary
collection contains 311 tests: 266 pass and 45 fail in eight files. The failures
are test-harness drift, not newly observed route drift:

- 33 assertions use June 2026 fixture dates or `date.today()` morning slots
  that are now past under the accepted temporal guard; and
- 12 proposal requests omit the syntactically required proposal
  `Idempotency-Key` introduced before this review.

A 184-test current subset covering raw compatibility modes, audit attribution,
temporal guards, status/delete behavior, rollback, waiting-area behavior and
the dormant scaffold passes. The stale tests remain named obligations; the
next gate repairs their clocks/headers before status-kernel work.

## Current behavior matrix

| Family | Success response | Mutation/audit | Current command idempotency | Current control gap |
|---|---|---|---|---|
| create | `201 AppointmentOut` | appointment plus `create` audit, `raw_compat_create` in default audit mode | none; no receipt/replay | precondition, separate confirmation, identity; also needs a future schedule fence |
| update | `200 AppointmentOut` | appointment plus `update` audit, `raw_compat_update` | none; no receipt/replay | precondition, separate confirmation, identity; target and schedule serialization |
| status | `200 AppointmentOut` | appointment plus `status_change` audit, `raw_compat_status` | none; no receipt/replay | precondition, separate confirmation, identity |
| delete | `204`, empty body | soft-cancel plus `delete` audit, `raw_compat_delete` | none; no receipt/replay | precondition, explicit destructive confirmation, identity |

All four authenticate and authorize a mutating role before entering the route,
scope resource lookup by the current practice, perform route-specific
validation, and commit mutation plus audit together in their helper. None
performs the accepted kernel's current-authority recheck and canonical locking
inside a single command transaction.

## Why status first

Status is the narrowest safe family foundation because both ingresses already
share one mutation helper and the accepted lock profile is practice,
appointment, then idempotency record. It avoids create's absent target row and
schedule fence, update's schedule-domain serialization, and delete's
destructive-response adaptation.

The first slice must nevertheless be confirm-first. The raw status route has no
place to obtain the three missing control groups without changing its ingress
contract. Running it through a kernel with invented evidence would be false
convergence; requiring new evidence without a consumer transition would be an
unreviewed compatibility break.

## Parent-contract source rebind

The review found that the accepted kernel-interface validator still expected
the pre-parity hashes of the deprecation map and consumer-readiness document.
Those documents were deliberately updated when native-client parity passed.
The two root SHA-256 bindings and their exact downstream hash-only bindings are
refreshed through the pure-adapter contract, shadow architecture, shadow
evidence and runtime-instrumentation architecture. All original source HEADs
and semantic fields remain unchanged. This repairs validation continuity
without rewriting accepted history or widening authority.

## Deliberate non-conclusions

- Zero committed system callers is not zero external callers.
- Test callers are evidence assets, not deployed clients.
- Direct database fixture creation is not a compatibility route and is not
  permission to bypass a production command kernel.
- Preserving a missing idempotency contract is not a goal. The future route
  transition must explicitly add it.
- This review does not decide whether unusual terminal-status re-transitions
  remain warn-and-confirm or become invalid.
- This review does not enable the dormant shadow scaffold or use operational
  observations.
