# Provider-free unmounted legacy-route convergence kernel design

Date: 2026-08-12

Status: `frozen_unmounted_design`

## One mutation kernel, several ingress adapters

The kernel owns semantics, not HTTP compatibility. A route adapter may parse a
route-specific envelope and name its canonical operation, but it cannot change
authority, outcome precedence, lock order, confirmation policy, freshness,
idempotency or audit meaning.

Proposal routes stop before the kernel. They may prepare an opaque backend
precondition and a separate confirmation envelope. Only a valid confirm or
future fully admitted compatibility adapter may construct a kernel request.

## Kernel phases

1. admit the closed structure and exact practice/actor/session/purpose/
   operation/target/conflict-domain/command-digest bindings;
2. resolve current actor authority before any stored-receipt disclosure;
3. validate separately required confirmation evidence;
4. resolve same-digest replay or different-digest idempotency conflict;
5. validate source-state and conflict-domain preconditions;
6. enforce current schedule and operation-specific domain invariants;
7. under canonical `practice -> schedule domain -> appointment -> idempotency`
   locking with unused locks skipped, stage the mutation, mutation audit and
   completed idempotency receipt; and
8. atomically commit and return readback, or return one typed loser with no
   mutation.

The accepted 2026-08-12 architecture controls the canonical lock order. Older
appointment-idempotency documents remain valuable historical storage evidence,
but their ledger-first ordering does not override this newer source-owned-truth
decision. A future implementation must reconcile existing helpers to one order
before mixed paths can execute.

## Required ingress evidence

| Concern | Proposal/confirm target | Raw compatibility target | Non-equivalence rule |
|---|---|---|---|
| Confirmation | explicit confirmer plus backend evidence | same separate evidence is required before eligibility | request arrival, route verb and authentication alone are not confirmation |
| Freshness | opaque backend precondition echoed at confirm | an equivalent expected source/conflict binding is required | a current read without a prior expected binding cannot prove the user's view was current |
| Idempotency | required durable command identity and digest | same command-grade identity and digest required | UI retry behavior and correlation ids are not idempotency |
| Audit | actor/practice/operation/target/result and receipt correlation | identical semantic fields with raw adapter attribution | a deprecation tag is not a mutation audit |

## Operation profiles

- **Create** has a null appointment target, requires schedule-domain
  serialization and is blocked from raw convergence until a reviewed
  database-owned fence exists.
- **Update** requires the schedule domain and target appointment and preserves
  their canonical ordering.
- **Status** requires the target appointment but no schedule-domain lock unless
  a separately reviewed status transition changes schedule occupancy.
- **Delete/cancel** requires the target appointment and explicit destructive
  confirmation; retained-history policy remains backend-owned.

## Typed result and audit boundary

`committed` owns the only first-effect ribbon: durable command receipt,
mutation-audit reference and current readback. `idempotent_replay` returns the
original receipt and a replay observation without another domain mutation audit.
Every loser result has no mutation and no success receipt. Operational/security
decision logging may describe the rejected attempt but cannot resemble a
completed appointment mutation.

The minimized target audit fields are practice, actor, role-at-decision,
canonical operation, route-adapter identity, target or conflict domain,
command digest, idempotency-key digest, precondition version/digest,
confirmation reference/mode, typed result, correlation id, timestamp and the
applicable audit/receipt identifiers. Raw request bodies, confirmation tokens,
credentials and patient-facing free text are excluded.

## Compatibility posture

The current raw routes stay operational and unchanged outside this design. The
contract records their missing kernel-grade evidence rather than inventing a
legacy bypass mode. A later shadow comparison may reveal what an adapter would
produce but must not gate, mutate or alter the response. Client parity and
route-specific ingress controls must then pass before a raw path can execute
through the kernel.

Deprecation remains a consequence of proven convergence, not a mechanism for
achieving it. `appointment_raw_compat_mode` stays `audit`; neither `header` nor
`off` is opened here.
