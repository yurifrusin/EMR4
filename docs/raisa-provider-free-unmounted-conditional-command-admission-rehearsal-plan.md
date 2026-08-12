# Provider-free unmounted conditional-command admission rehearsal plan

Date: 2026-08-12

Source HEAD: `b9a94a90a21c532f7fda55f9d18ba00156b123b3`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Mechanically instantiate the accepted source-owned-truth conditional-command
architecture without opening a route, database, event source or write. The
rehearsal proves that malformed or widened packets stop before command
evaluation and that structurally admitted authored-synthetic packets resolve
to one exact non-ambiguous outcome under a frozen precedence.

## Narrow boundary

One pure in-memory evaluator consumes closed authored-synthetic cases. It may:

- validate backend-minted precondition bindings against a request;
- validate operation-specific target and canonical lock plans;
- compare synthetic current-authority, source-state, conflict-domain,
  confirmation, idempotency and domain-invariant facts;
- return one typed admission decision and, only when admitted, one typed command
  outcome; and
- describe a planned effect without performing it.

It cannot sign or verify a real token, take a lock, query a source, consume an
event, execute a route, mutate state or issue an audit/command receipt.

## Frozen precedence

The evaluator applies these phases in order:

1. closed structure, token authenticity flag, version/expiry and exact request
   bindings;
2. operation target shape, target existence expectation and exact canonical
   lock plan;
3. rejection of any event offered as current truth or command evidence;
4. current authority;
5. required confirmation;
6. idempotency replay/conflict;
7. source-state and conflict-domain freshness;
8. current schedule and domain invariants; and
9. planned `committed` outcome.

Structural/binding failures return `admission_rejected` plus exact reason codes
and no command outcome. Admitted cases return exactly one of the eight outcomes
frozen by the accepted architecture. Only `committed` reports
`planned_mutation: true`; even then the rehearsal performs no mutation.

## Required scenario census

The canonical packet must include at least:

- clean create, update, status and delete plans;
- same-digest idempotent replay and different-digest idempotency conflict;
- stale source state and stale schedule-conflict domain;
- current schedule conflict, revoked authority, missing confirmation and domain
  validation failure;
- expired or invalid-signature token;
- practice, actor/session, purpose, operation, target, conflict-domain and
  command-digest binding mismatches;
- create without the schedule-domain fence;
- update/status/delete target or lock-plan failure;
- non-canonical lock ordering; and
- an event offered as truth or command-success evidence.

## Owned files

- `docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-plan.md`
- `docs/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-design.md`
- `docs/security/raisa-provider-free-unmounted-conditional-command-admission-rehearsal-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-unmounted-conditional-command-admission-rehearsal/scenarios.json`
- `orchestration/continuity/raisa-provider-free-unmounted-conditional-command-admission-rehearsal/scenarios.schema.json`
- `scripts/raisa_provider_free_unmounted_conditional_command_admission_rehearsal.py`
- `tests/test_raisa_provider_free_unmounted_conditional_command_admission_rehearsal.py`
- exact receipts, review if risk-triggered, closeout, acceptance, Yuri mailbox,
  Continuity/Compass updater and lifecycle tests if the rehearsal passes.

## Forbidden surfaces

- no route, UI, database, source, listener, watcher, worker or migration;
- no real event, token, signature, lock, command, mutation, receipt or audit;
- no provider/model call unless a final independent veto is risk-triggered
  after all deterministic gates;
- no patient, clinical, product-derived, financial or licensed content;
- no credential, IAM, metadata, network, executable or tool;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad Git staging or staging of `docs/branding/` or unrelated untracked
  files.

## Acceptance

The tranche passes only when:

1. the scenario packet validates against a closed schema and exact accepted
   architecture-contract SHA-256;
2. all required operations, outcomes and failure families are represented;
3. every canonical scenario returns the exact expected decision, outcome,
   reason codes and planned-mutation flag;
4. structural rejection never produces a command outcome;
5. only admitted `committed` reports a planned mutation and no scenario performs
   an effect;
6. create requires a schedule-conflict-domain fence while the other operations
   retain their exact target/lock requirements;
7. current authority precedes receipt replay and other potentially revealing
   outcomes;
8. event evidence can never satisfy freshness, authority, confirmation or
   command success;
9. at least twenty independent hostile mutations fail closed;
10. focused tests, canonical repository checks and Git whitespace pass; and
11. protected refs and all unrelated untracked files remain unchanged.

## Recovery and next work

A mechanical defect in the packet, schema, evaluator or test may receive one
bounded correction while the frozen precedence and claim boundary remain
unchanged. A need to alter architecture meaning stops the rehearsal for a
separate architecture decision.

After acceptance, the next candidate is a provider-free unmounted legacy-route
convergence map and kernel-interface design. It may map all four raw routes and
their proposal/confirm replacements onto one abstract conditional-command
interface, but still may not change route or database behavior.
