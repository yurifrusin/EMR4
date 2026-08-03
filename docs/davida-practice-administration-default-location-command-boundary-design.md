# Davida default-location proposal-to-confirm command-boundary design

Date: 2026-08-03

Boundary classification:
`architecture_only_backend_owned_default_location_command_boundary`

## API Spine topology

```text
accepted Davida dry-run candidate (non-authoritative, proposal-only)
  + authenticated EMR4 practice-administration session
  -> POST .../default-location/proposals       [non-mutating]
       fresh authorize -> fresh scoped read
       -> deterministic signed self-contained proposal reference + expiry
  -> explicit human practice-manager/owner action
  -> POST .../default-location/proposals/{proposal_id}/confirm
       authenticate/authorize before disclosure
       -> bind and revalidate proposal + expected aggregate version
       -> reauthorize exact practice/action/resource inside transaction
       -> one future atomic aggregate/audit/outbox/idempotency transaction
       -> bounded receipt
       -> outbox publication after commit only
```

GraphQL remains read-only. The two paths are documented in a separate OpenAPI
artifact so the accepted appointment command contract is unchanged. The
artifact uses an `.invalid` documentation server and explicitly has no runtime
mount or implementation claim.

## Proposal phase

The proposal endpoint is a non-mutating command-style read. Its authenticated
human request is bound to exactly one practice, practitioner aggregate,
requested active location, dry-run/context revision and expected aggregate
version. The backend authorizes the practice-level propose action before
resource disclosure, then reads current truth within that practice and
recomputes:

- the exact before and after location references;
- the canonical changed path `practitioner.default_location_ref`;
- the before-state hash;
- the deterministic proposal hash; and
- an expiry no later than both the dry-run expiry and 120 seconds after the
  backend's evaluation time.

`proposal_id` is a backend-issued signed opaque self-contained reference. It
covers the practice, practitioner, requested location, expected version,
proposal hash and expiry, and is verified on confirmation without a proposal
store. It is neither a reservation nor a durable proposal row.

The proposal header supplies syntactic idempotency discipline and correlation.
Identical calls deterministically re-evaluate; there is no proposal ledger,
reservation, lock, command claim or database change. The response has
`applies_change=false`, `davida_can_confirm=false`, and human confirmation is
required. Davida provenance may be recorded as `delegated_agent=davida`, but it
never becomes actor or confirmation authority.

Practice, actor and role are derived from the authenticated application
session, never trusted from JSON. The request body contains only a binding
assertion; every echo must exactly match session-derived authority or the
request rejects before resource disclosure.

## Confirmation and fresh authorization

The proposed future contract permits only an authenticated `human_user` with a
current same-practice `practice_manager` or `practice_owner` authorization to
confirm. This is future contract policy, not evidence that today's prototype
permission matrix or any mounted runtime already grants the action. The backend:

1. authenticates the application session;
2. authorizes the practice/action class before loading the resource;
3. validates canonical request shape and exact practice/proposal/aggregate
   bindings;
4. begins the future command transaction and claims the scoped idempotency key;
5. locks the practitioner row within the exact practice;
6. rechecks the role/action/resource decision immediately before mutation;
7. verifies proposal hash, expiry, confirmation evidence, expected aggregate
   version, before-state hash, active location and no-op/conflict rules; and
8. either rejects without effect or executes the single atomic unit below.

The request carries only an opaque backend-issued, short-lived, server-held,
single-use application-session confirmation-evidence reference. The trusted
server-side record covers the proposal and canonical confirmation payload.
Client-supplied structure, hashes, roles, signatures or Davida output cannot
mint evidence.

## Durable idempotency and replay

The confirmation key is scoped to practice, operation and authenticated human
actor. The ledger fingerprint binds the canonical request body and proposal
hash.

- same scope, key and fingerprint: return the already stored bounded domain
  receipt; no second aggregate/audit/outbox effect;
- same scope and key, different fingerprint: `idempotency_conflict`;
- different key with an already consumed single-use confirmation-evidence
  nonce:
  `confirmation_replay_rejected`;
- in-progress key: fail closed as `idempotency_in_progress`; and
- infrastructure failure before commit: no completed key or receipt and no
  partial state.

The transport may label a replay, but the stored domain receipt is unchanged.

## Atomic future transaction

One serializable or equivalently guarded transaction must:

1. claim/lock the idempotency row;
2. claim the unique single-use confirmation-evidence nonce;
3. lock and change exactly one practitioner default-location field;
4. increment the aggregate version exactly once;
5. append exactly one immutable audit event;
6. append exactly one transactional outbox event; and
7. complete the idempotency row with the bounded receipt.

Commit makes all seven durable together. Any exception, failed invariant,
authorization loss, version mismatch or conflict rolls all seven back. The
outbox event is eligible for publication only after commit; it is a signal,
never truth or command authority.

## Bounded receipt

The receipt contains opaque practice/practitioner/location references,
proposal and canonical request hashes, expected and resulting aggregate
versions, correlation and receipt identifiers, a hash of the idempotency key,
the authenticated confirmer reference/role, audit and outbox event identifiers,
commit time, and closed verification booleans. It contains no free text,
display name, raw session credential, patient/clinical/document data or event
payload. Rejected results contain a closed reason code and no success receipt.

## Rejections

The closed vocabulary distinguishes unauthenticated/unauthorized admission,
scope and resource mismatch, inactive or foreign location, no change, expired
or hash-invalid proposal, aggregate-version or before-state conflict,
confirmation-evidence failure, idempotency conflict/in-progress, replay, and
atomic transaction failure. Authorization failures are anti-enumerating.

## Authority ceiling

This artifact freezes a future backend contract; it does not implement it.
Davida remains proposal-only and cannot confirm, apply, call commands, hold
credentials or acquire database/event authority. No provider/model,
memory/RAG, real identity/data, patient/clinical/document data, arbitrary API,
GraphQL mutation, migration, runtime route, deployment, production or release
gate is opened. `docs/branding/` remains excluded.
