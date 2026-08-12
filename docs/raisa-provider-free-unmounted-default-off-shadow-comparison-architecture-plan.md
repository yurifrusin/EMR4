# Provider-free unmounted default-off shadow-comparison architecture plan

Date: 2026-08-12

Source HEAD: `71e240218b1adf1214fff87b542a9d0f6764230e`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Freeze the smallest architecture by which a future raw appointment route may
be observed against the accepted pure adapter without changing what the route
does. The result is static and authored-synthetic. It wires no route and
creates no observer runtime.

## Boundary classification

This is a diagnostic observation boundary beside the REST/OpenAPI command
plane, never part of command admission:

- the authoritative handler completes and seals its result first;
- a post-result hook may receive only an immutable minimized projection;
- explicit global, practice, route and generation controls must all admit the
  observation, with every unknown or missing control denying it;
- the observer may run the pure adapter and compare structural/gap evidence;
- its only output is a minimized diagnostic record or no record; and
- no observer state, result, failure, timeout or overflow may feed back into
  request, response, audit, transaction, command or client behavior.

## Frozen scope

Only the four raw compatibility adapter identities are in scope:

- `raw_compat_create`;
- `raw_compat_update`;
- `raw_compat_status`; and
- `raw_compat_delete`.

Confirm and proposal routes are excluded because their pure mapping already
passed and the migration question is the gap on raw compatibility ingress.

## Default-off control

Observation requires the intersection of:

1. immutable-generation status `current`;
2. global feature value `enabled`;
3. practice feature value `enabled`; and
4. exact route-adapter membership in the generation allowlist.

The frozen architecture defaults the global and practice values to `disabled`
and the route allowlist to empty. Missing, unknown, stale, superseded or revoked
state returns `disabled_no_observation`. A separately owned external kill
switch may only disable; it cannot enable.

## Data minimization

The future hook may receive only closed fields needed to reproduce the pure
adapter's structural decision: versioned one-way practice, actor, session,
target, conflict-domain and correlation digests; role/purpose and target-shape
labels; command/precondition/idempotency digests and non-secret versions;
confirmation mode plus a confirmation-reference digest; and presence bits for
the three control groups.

Raw request/response bodies, patient identity, free text, direct product IDs,
credentials, tokens, source state, authority decisions, database values and
mutation/audit receipts are forbidden. This tranche uses only `syn-` labels.

## Non-enforcement invariants

The future observer:

- starts only after the primary status, body, headers and transaction
  disposition are sealed;
- has no reference to the response writer, transaction/session, command
  service, source adapter, event bus, audit writer or kernel entry point;
- has no synchronous return path to the handler;
- uses a bounded best-effort one-way handoff with overflow/drop permitted;
- catches observer/comparison/sink failure inside the boundary;
- cannot add deprecation headers, reject or retry a request, alter latency
  budgets, grant kernel eligibility or emit a command outcome; and
- treats data loss as acceptable because this is diagnostic evidence, never
  correctness or audit evidence.

## Owned files

- this plan;
- `docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture.md`;
- `docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture/contract.json`;
- its closed schema;
- `scripts/raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py`;
- `tests/test_raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py`;
- exact receipt, closeout, acceptance, Yuri mailbox, Continuity/Compass updater
  and lifecycle test artifacts if the tranche passes.

## Forbidden surfaces

- no import, execution, edit, wrapping or instrumentation of an application
  route;
- no observer, queue, hook, sink, feature flag or runtime wiring;
- no database, source, watcher, event, transaction, response or audit access;
- no provider, network, credential, IAM or metadata access;
- no product-derived, patient, clinical, financial or free-text data;
- no executable tool, kernel invocation, command, write or mutation;
- no client change, header, deployment, production, release, Pages rebuild or
  protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated
  untracked file.

## Acceptance

The tranche passes only when:

1. one closed schema validates one exact source-hashed architecture contract;
2. scope is exactly the four accepted raw adapters and no proposal/confirm
   adapter is admitted;
3. global, practice, route and immutable-generation controls form a four-way
   intersection with default denial and disable-only kill switch;
4. the primary result is sealed before observation and no feedback edge exists;
5. input and output fields are exact, minimized and prohibit raw bodies,
   direct identifiers, patient/free text, tokens, source state and receipts;
6. comparison classes distinguish expected current gaps, unexpected gaps,
   unexpected candidate, projection divergence and observer failure without
   emitting a command outcome;
7. queue overflow, timeout and all observer/sink failures can only drop the
   diagnostic record;
8. the observer has no kernel, command, source, response, transaction, audit,
   event or eligibility capability;
9. at least thirty independent hostile mutations fail closed;
10. focused API Spine, repository-profile and Git whitespace checks pass; and
11. protected refs and every pre-existing untracked file remain unchanged.

## Recovery and next work

A mechanical schema, fixture, validator or assertion defect may receive one
bounded correction without changing the four-way enablement intersection,
post-result placement, minimization or no-feedback rule. Any request for
synchronous enforcement, raw payload retention, route behavior change, kernel
invocation or runtime wiring is conceptual and must stop this tranche.

After acceptance, the next safe candidate is the provider-free unmounted
authored-synthetic shadow-comparison rehearsal. It may exercise disabled,
admitted, expected-gap, divergence, failure, timeout and overflow scenarios
against this architecture, but still may not import or execute an application
route, source, database, event, watcher or command.
