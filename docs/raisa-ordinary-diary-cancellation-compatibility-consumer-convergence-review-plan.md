# Ordinary Diary cancellation compatibility-consumer convergence review plan

Date: 2026-08-17

Timestamp: 2026-08-17T17:09:51.0737699+10:00 (Australia/Brisbane)

Status: `frozen_for_repository_static_execution`

Task baseline: `36b116bdb72c82acac63b8a0371d6212e9bc1f9a`

Target result:
`raisa_ordinary_diary_cancellation_compatibility_consumer_convergence_review_pass`

Reasoning level: Extra High. The tranche changes no product source, but it
selects the later convergence meaning for a destructive compatibility
consumer and must distinguish a committed-write response mismatch from a
failed command.

## Objective

Inventory `deleteBooking()` and `applySignedDeleteProposal()` against the exact
accepted canonical delete-only consumer contract now exercised by Reception
One. Determine the smallest later client-source convergence that removes
dual-family cancellation, admits only the strict minimal public receipt and
reconciles current truth after every terminal or uncertain outcome.

This review performs no HTTP request and changes no product, route, OpenAPI,
schema, service, migration, database or UI source.

## API Spine classification

- Boundary: destructive REST/OpenAPI appointment command consumer.
- Accepted pattern: one dedicated delete proposal, explicit human
  confirmation, one canonical delete-confirm command, backend current-truth
  and current-authority recheck, strict public receipt, then a fresh scoped
  read.
- GraphQL and events: unchanged and never command authority.
- Compatibility status: raw `DELETE`, status-cancel fallback and hyphenated
  confirm alias remain inventory facts only; none is admitted for a new or
  converged client.

## Exact read-only evidence

1. `docs/diary/diary.js` at Git blob
   `a01733a6b543c250d7f7db4d7ca93a6e8474143c`, limited to the canonical
   cancellation bridge, `deleteBooking()`, `applySignedDeleteProposal()`, the
   confirm allowlist and strict public-envelope validator;
2. `app/routers/appointments.py` at Git blob
   `486ab53b083d36de3ac5cd346627de79e2f897b8`, limited to the mounted delete
   proposal/confirm route and returned public envelope;
3. `app/schemas/appointments.py` at Git blob
   `71eb29aac83dd76ca82c27b5a31079db9e813827`, limited to the strict delete
   receipt/envelope types;
4. `docs/api-spine/openapi/appointment-commands.yaml` at Git blob
   `9795f0e6624ec1081c4102c2b48377b5448b8b3e`, limited to delete proposal,
   canonical confirm and response schemas;
5. the accepted cancellation readiness, delete route/product-adapter and
   Reception One cancellation plan/closeout chain; and
6. focused ordinary Diary, delete-confirm and API Spine tests named by the
   report.

No protected evidence, historical Diary material, product/database state or
provider output is eligible.

### Bounded verification containment

The first broader packet found that
`tests/test_api_spine_delete_confirm_idempotency_route_contract.py` still
defaulted its otherwise valid delete-confirm fixture to a null structured
reason. The accepted dedicated contract now default-denies that historical
shape. A reason-only test repair then exposed deeper pre-adapter session,
current-authority and HTTP-shape assumptions. That attempted change is reverted;
the legacy suite is explicitly excluded from this review and retained as future
test-harness debt. Current accepted route-convergence/product-adapter tests are
the backend control. No product or API source is opened.

## Questions and decision rule

The review must answer:

1. Which cancellation family does each ordinary consumer admit?
2. Does a 404 or error cause semantic fallback, and which fields are lost?
3. Does the dispatcher validate proposal identity, command meaning, endpoint
   and reason fields before confirmation?
4. Does it accept the canonical recursively closed public envelope or still
   require an appointment read model?
5. Does every success, block, cancellation, response loss, transport failure
   or malformed response force fresh authorised reconciliation before another
   action?
6. Can the smallest later change be confined to `docs/diary/diary.js`, its
   cache reference if required, and focused tests?

Select exactly one later convergence. It must preserve the dedicated backend
contract unchanged, fail closed rather than fall back to status or raw delete,
reuse the strict proposal/receipt validators where practical, and avoid
optimistic mutation. A product-source edit is expressly deferred to that later
tranche.

## Acceptance

The review passes only if it:

1. cites both ordinary functions and the canonical Reception One bridge;
2. distinguishes pre-command failure from unknown post-command outcome;
3. proves or rejects direct compatibility with the current public envelope;
4. records all dual-family, reason-preservation, confirmation, idempotency,
   response and reconciliation differences;
5. freezes one minimal later source/test boundary with explicit fail-closed
   behavior;
6. adds deterministic static assertions for the current facts and report;
7. changes no product/API/runtime source;
8. passes the focused review test, current route-convergence/API Spine artifact
   tests, JavaScript syntax, canonical fast profile and Git whitespace; and
9. receives one fresh Gemini 3.7 Flash/high exact-candidate read-only veto after
   deterministic admission because destructive compatibility semantics are a
   material independent-review surface.

Evidence label: `repository_static_authored_synthetic`.

## Parallelism-efficacy allocation

- **Sol:** owns the tightly coupled two-function semantic inventory, later
  boundary selection, report, deterministic admission, acceptance and Git.
- **DeepSeek V4 Flash/high:** declined. There is no separable implementation;
  mechanical extraction would not offset packet and reconciliation cost.
- **Gemini 3.7 Flash/high:** reserved for one fresh exact-candidate read-only
  veto after deterministic admission.
- **Native subagents:** declined because current developer policy prohibits
  proactive native delegation.

Reassess at report freeze, material recovery, pre-verifier admission and
closeout. Repository pytest remains serial through the admitted wrapper.

## Claim and closed surfaces

Passing proves repository facts and freezes the next client-only convergence.
It does not prove or change live behavior, database effects, representative
usability, external adapter compliance, deployment or production.

No raw compatibility DELETE or status-cancel call, product source edit,
provider/ADC, credential/IAM, external network, database/source/watcher access,
patient/product/clinical/historical data, executable model tool, deployment,
production, release, Pages or protected-ref movement is authorised.
`docs/branding/` and every unrelated untracked file remain preserved;
explicit-path staging only.
