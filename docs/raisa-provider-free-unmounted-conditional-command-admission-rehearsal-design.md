# Provider-free unmounted conditional-command admission rehearsal design

Date: 2026-08-12

Status: `frozen_unmounted_design`

## Packet model

Each scenario contains four authored-synthetic objects:

- `token`: the backend-owned precondition claims plus a synthetic authenticity
  flag;
- `request`: the echoed bindings, idempotency identity and separately supplied
  confirmation evidence;
- `current`: the synthetic command-service view of authority, state,
  idempotency and invariants; and
- `lock_plan`: the ordered names the eventual transaction would acquire.

The evaluator returns `admitted` or `admission_rejected`. Rejection carries
sorted exact reason codes and no command outcome. Admission carries exactly one
of the architecture's eight outcomes. It also reports whether an effect would
be planned; it never performs the effect.

## Binding admission

The token and request must agree on practice, actor/session, purpose, operation,
target appointment, schedule-conflict domain and command digest. The token must
use the supported schema/token versions, a recognised synthetic signing key,
an unused nonce, a valid authenticity flag, and an interval containing the
synthetic current time.

Target shape is operation-specific. Create requires a null appointment target
and a schedule-conflict domain. Update requires a non-null target and both the
schedule domain and appointment lock. Status and delete require a non-null
target and omit the schedule-domain lock. All lock plans preserve the accepted
global order after unused entries are removed.

## Outcome evaluation

After admission:

1. revoked current authority returns `authority_revoked`;
2. absent/invalid required confirmation returns `confirmation_required`;
3. a same-digest completed idempotency record returns `idempotent_replay`, and a
   different digest returns `idempotency_conflict`;
4. changed source state or conflict-domain state returns
   `stale_precondition`;
5. a current schedule overlap returns `schedule_conflict`;
6. missing target state or another current domain failure returns
   `validation_rejected`; and
7. otherwise the result is `committed` with a planned mutation only.

This ordering prevents a revoked actor from learning an original receipt and
prevents stale evidence from outranking current source invariants. It is a
rehearsal contract, not a claim about HTTP status codes or production response
wording.

## Evidence boundary

All identifiers use the `syn-` namespace. Digests are fixed non-secret labels,
timestamps are fixed UTC values and the signing/authenticity fields are inert
booleans or identifiers. No cryptography, route import, application model,
database driver, network library or provider client is used.
