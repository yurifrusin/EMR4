# Provider-free globally-disabled runtime-instrumentation scaffold plan

Date: 2026-08-12

Source HEAD: `b74c0821fc8c819910756a354245c32b5a0a7f82`

Status: `frozen_for_bounded_implementation`

## Purpose

Implement the narrowest typed application scaffold allowed by the accepted
source-bound runtime-instrumentation architecture while making operational
observation structurally impossible. The default application must remain
globally disabled and attach no observer or sink.

## Frozen implementation

### Closed generation

Add one immutable `ShadowInstrumentationGeneration` and a static reader. In
this tranche the type rejects every enabled generation, non-empty practice or
route allowlist and non-null digest-key reference. The only application
generation is therefore process-start immutable, globally disabled, empty and
credential-free. A monotonic latch may move only from clear to disabled.

No environment variable, mutable feature service, database lookup or
`appointment_raw_compat_mode` coupling is added.

### Typed seams

Add one product-independent module containing:

- the closed immutable generation and reader;
- `ServerOwnedShadowRequestContext` and a context-provider protocol, but no
  provider implementation;
- the exact 24-field immutable `ShadowRouteProjection`;
- an input type limited to closed structural fields and an injected digest-port
  protocol, with no concrete key or credential implementation;
- a pure projection factory;
- a request-scoped single-assignment, take-and-clear cell;
- a no-result `ShadowOfferPort` protocol and a closed implementation that
  rejects every direct offer;
- a route-stage runtime whose disabled check precedes context, projection,
  digest and cell access; and
- a pure ASGI finalizer that delegates directly when disabled and otherwise
  orders original final-body send before one contained, non-awaiting offer.

The application cannot construct the finalizer's admitted branch in this
tranche. Its ordering is exercised only through authored-synthetic unit probes.

### Exact application edits

Mount the pure ASGI middleware last in `app/main.py`, making it outermost around
the existing CORS/error stack. Because the only generation is disabled, it must
delegate without allocating a cell or wrapping `send`.

At each accepted route seam in `app/routers/appointments.py`, replace the direct
helper return where necessary with a local result, call the no-result route
stage after helper success, then return the same object. Delete keeps its
implicit `None` after helper success and staging. The route stage receives only
the closed adapter ID; no body, user, response, database/session, identifier,
context supplier or projection supplier is passed.

## Authored-synthetic evidence

Unit evidence must prove:

1. enabled/allowlisted/key-bearing generations cannot be constructed;
2. the disable latch cannot re-enable;
3. disabled stage calls invoke zero context, projection or digest suppliers and
   create/store no request cell;
4. disabled middleware produces the exact original ASGI message sequence and
   makes zero offer calls;
5. the cell is single-assignment, take-and-clear and at-most-once;
6. the finalizer sends the final body first and contains a later offer failure;
7. the pure factory emits exactly the accepted 24 fields from authored-
   synthetic structural input and has no free-text/response input surface;
8. AST evidence binds all four stage calls after helper success and before the
   unchanged return form;
9. the default application middleware order is shadow, CORS, error handler;
10. create/update/status/delete route tests preserve status, response shape,
    headers, database result and one attributable audit without any staged cell
    or offer; and
11. validation/auth/conflict/helper/serialization failure paths cannot emit an
    offer.

## Owned files

- this plan and its design/threat delta;
- `app/services/diary/shadow_instrumentation.py`;
- `app/middleware/shadow_instrumentation.py`;
- the exact bounded edits to `app/main.py` and
  `app/routers/appointments.py`;
- `tests/test_raisa_provider_free_globally_disabled_runtime_instrumentation_scaffold.py`;
- exact receipt, closeout, acceptance, Yuri mailbox and lifecycle artifacts.

## Forbidden surfaces

- no enabled generation, practice or route;
- no environment/config toggle, database/network flag lookup or mutable
  generation;
- no server-owned context implementation and no bearer-token, inbound-header or
  actor/practice-derived session fallback;
- no observer, adapter invocation, sink, queue, thread, process, persistence,
  retention, aggregation or monitoring;
- no operational database/source/watcher/event/provider/network or credential
  access;
- no real product, patient, person, clinical, financial or free-text data;
- no response/body/header material in the projection or offer;
- no kernel, executable tool, new command/write authority, deployment,
  production, release, Pages or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated untracked
  file.

## Acceptance and recovery

The tranche passes only if every item in the authored-synthetic evidence list,
focused API Spine/route tests, lifecycle checks and canonical fast profile pass;
the application generation is provably unenableable; exact route response,
header, audit/commit and error behavior remains unchanged; and all protected
refs/untracked files remain preserved.

One bounded mechanical correction may repair typing, import order, middleware
registration, stage placement, a test fixture or a closed assertion. Any need
to enable configuration, infer request identity, pass product material to the
stage, attach an observer/sink, await an offer, retry, persist evidence or let a
shadow result affect response/audit/transaction/command behavior is conceptual
and stops this tranche.

After acceptance, the next planned gate is ordinary/fallback client
proposal-confirm parity. It must first freeze which client paths still use raw
writes and prove their proposal/confirm replacements without removing or
blocking compatibility routes. No raw-route kernel convergence begins in this
scaffold.
