# Provider-free compatibility-consumer and kernel-convergence admission review plan

Date: 2026-08-12

Source HEAD: `3be9a06cbe24d388ccf49631dbd54321fe3a9319`

Status: `frozen_for_read_only_static_review`

## Purpose

Determine what still depends on the four raw appointment compatibility writes,
freeze the public and transactional behavior a later convergence must account
for, and select the narrowest first status/delete/update slice before create.
This review changes no route, kernel, client, database or command behavior.

## Inventory method

The review examines the complete Git-tracked repository and distinguishes:

1. deployed product/runtime HTTP consumers;
2. import, recovery, migration and operational-system HTTP consumers;
3. executable conformance tests and review probes;
4. static contracts and route declarations;
5. direct database fixture/bootstrap writers that do not call a route; and
6. external consumers that repository inspection cannot identify.

The exact source-bound result is
`orchestration/continuity/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review/consumer-and-preservation-inventory.json`.
Absence from the committed repository never proves absence outside it.

## Frozen admission result

- The native Diary has zero raw appointment mutation calls.
- No committed product/runtime, import, recovery, migration or operational
  script calls any of the four raw HTTP routes.
- Exactly 126 direct raw-route HTTP call expressions remain across 21 tracked
  test/review files. They are conformance consumers, not deployed product
  callers, and must be retained or deliberately migrated with the behavior
  they witness.
- A broad 311-test collection across the 20 ordinary test files has 266
  passing tests and 45 stale harness failures in eight files. Thirty-three
  failures use fixed past dates or same-day times that have already elapsed;
  twelve proposal failures omit the now-required proposal idempotency
  header. A current 184-test raw compatibility, audit, temporal, status and
  waiting-area baseline passes. No current safety control is weakened to make
  the stale tests pass.
- `seed.py` and three authored-synthetic acceptance harnesses create
  appointment rows directly. They are not compatibility-route consumers. They
  remain explicit fixture/bootstrap obligations and gain no command authority.
- External consumers remain `unknown_without_operational_observation`.
  Therefore all four routes remain mounted and `appointment_raw_compat_mode`
  remains `audit`.
- The accepted kernel-interface validator exposed stale hashes for the two API
  Spine declarations changed by the accepted client-parity descendant. This
  review rebinds those two hashes and follows their deterministic hash-only
  cascade through the pure-adapter, shadow architecture, shadow rehearsal and
  runtime-instrumentation architecture validators. Every original source HEAD,
  interface, scenario, outcome, lock order, migration DAG and route
  ineligibility remains unchanged.

## Behavior that later convergence must account for

Every later slice must begin from the exact current contract rather than
assuming raw and confirm behavior are already equivalent:

- create returns `201 AppointmentOut`; update and status return
  `200 AppointmentOut`; delete returns `204` with no response body;
- authenticated mutating roles and practice-scoped lookup remain required;
- request validation, tenant/resource checks, temporal rules, conflict rules,
  waiting-area behavior, status-reason policy and error status/detail shapes
  remain route-specific compatibility obligations;
- one appointment mutation and one attributable mutation-audit row commit
  together, or neither commits;
- default `audit` mode adds the exact `raw_compat_*` code to minimized audit
  evidence; `header` additionally emits the existing `Deprecation` header and
  `off` remains a diagnostic compatibility posture, not a migration target;
- raw routes currently require no command-grade `Idempotency-Key`, create no
  completed command receipt and do not provide replay semantics; and
- raw routes currently lack a prior backend precondition and separate
  confirmation evidence. Those gaps must not be relabelled as preserved
  safety. They are prerequisites for convergence and necessarily require a
  separately reviewed ingress transition.

The current commit boundary is also recorded honestly: the helper commits the
mutation and audit before route return/response serialization, and the dormant
shadow stage is called only after helper success. A later kernel may improve
unknown-commit handling, but it may not claim byte-for-byte transaction parity
if it deliberately changes that boundary.

## Selected first implementation family and slice

The first family remains **status**, consistent with the accepted
status -> delete -> update -> create dependency order. Status has one existing
target row, no schedule-domain lock for the currently admitted profile, and
the raw and confirm routes already share `_apply_appointment_status_update`.

The first implementation slice is narrower than raw-route convergence:

1. rehearse the provider-free, unmounted status transaction/kernel protocol;
2. reconcile authority-first evaluation with canonical
   `practice -> appointment -> idempotency record` ordering;
3. freeze atomic appointment, audit and completed-receipt behavior plus typed
   loser outcomes;
4. then, only under a separately accepted runtime tranche, place the existing
   status-confirm route behind that kernel while preserving its HTTP envelope;
5. keep raw `PATCH /api/v1/appointments/{appointment_id}/status` on its current
   helper and behavior until equivalent backend precondition, separate
   confirmation and command idempotency ingress has passed; and
6. do not begin delete, update or create convergence in the status slice.

The terminal-status re-transition warning and the dormant post-commit response
serialization boundary are explicitly retained as review questions. This
admission review neither fixes nor blesses them.

## Acceptance

The review passes only if:

1. the five-source Ariadne receipt passes;
2. all four raw routes, handlers, default signal mode and zero native-client
   raw calls remain source-bound;
3. the tracked executable consumer census is exact and rejects a new product,
   script, import, recovery or migration caller;
4. direct database fixture/bootstrap writers are named separately;
5. response, audit, idempotency and transaction facts are exact for all four
   routes;
6. unknown external consumers remain unknown and block retirement/header-mode
   rollout conclusions;
7. status is selected without implementing a kernel or changing raw `PATCH`;
8. focused API Spine/static tests and canonical repository checks pass; and
9. protected refs and every unrelated untracked file remain unchanged.

## Forbidden surfaces

- no route edit, removal, rename, blocking, alias or execution;
- no kernel, adapter, schedule fence, shadow enablement, observer or sink;
- no database/source/watcher/event, product/patient/clinical data or free text;
- no provider, credential, IAM, metadata or network access;
- no command/write expansion, deployment, production, release, Pages or
  protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated
  untracked file.

## Next safe descendant

After acceptance, the next dependency-satisfied tranche is a provider-free
compatibility conformance-harness temporal/idempotency readiness repair. It may
make only deterministic test-fixture changes: future-relative clinic-local
dates with frozen clocks where required, and non-empty proposal idempotency
headers. It must not change application behavior or expected route semantics.
Once the full 311-test baseline is green, the provider-free unmounted status
transaction-kernel protocol rehearsal is next. That protocol may use only
authored-synthetic closed state machines and transaction schedules; it may not
import or execute an application route, database, provider, event, watcher or
command.
