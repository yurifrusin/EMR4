# Provider-free unmounted status-confirm runtime convergence architecture

Date: 2026-08-12

Source HEAD: `fca97097eeca5070ad41e403aed9413eee45ccba`

Result: `raisa_provider_free_unmounted_status_confirm_runtime_convergence_architecture_pass`

Implementation authorized: `false`

## Decision

The nine route-to-kernel gaps now have one closed convergence architecture.
The status-confirm family is split at an explicit status-only discriminator,
then one backend-owned transaction performs ordered current-authority,
idempotency, freshness, confirmation, mutation, audit and receipt work. The
architecture preserves current waiting-area behavior outside this kernel and
changes no application or database code.

## Boundary

```text
signed confirmation transport
        |
        v
status-only discriminator ----> waiting-area sibling remains unchanged
        |
        v
server-owned authority/session ingress
        |
        v
practice -> appointment -> idempotency_record locks
        |
        v
current authority -> replay/conflict -> version -> warnings/evidence -> terminal
        |
        v
appointment mutation + attributable audit + completed receipt
        |
        v
one atomic commit -> exact stored canonical response for initial/replay delivery
```

The route and the intelligent layer remain outside the effect boundary.
GraphQL remains read-only, committed events remain cues for fresh authorized
reads, and mutation remains a single-purpose REST/OpenAPI command owned by the
backend.

## Closed contracts

### 1. Status-only discrimination

Only `update_appointment_status` can create a kernel ingress. The existing
`update_appointment_waiting_area` union sibling stops before ingress. This
avoids treating the whole confirmation-family schema as one write authority and
preserves waiting-area behavior until it has its own separately accepted path.

### 2. Server-owned current authority

The kernel accepts `practice_id`, `actor_id`, `actor_role`, `active_user` and an
opaque `session_binding_digest` only from backend authority/session services.
Client duplicates have no authority. After acquiring all status-subset locks,
the transaction rechecks those current facts before it classifies or discloses
an idempotency replay or conflict.

The digest is a binding reference, not a credential, session token or browser
secret. The completed private receipt may retain the digest for correlation;
the public response does not expose it.

### 3. Ordered transaction and disclosure

The exact status lock order is:

1. `practice`;
2. `appointment`; and
3. `idempotency_record`.

The unused schedule-conflict domain is skipped without reordering. Target
absence stops while attempting the appointment lock. Once all three locks are
held, current authority is rechecked before `inspect:idempotency`; therefore a
revoked caller receives neither a stored receipt nor a key/digest conflict.

### 4. Durable current-state identity

The locked appointment adapter must expose a positive monotonic
`appointment_state_version`. Every committed appointment state change advances
it. Signed evidence binds the proposed version, and the kernel compares it with
the version read under the appointment lock.

The architecture deliberately does not select a physical column, migration,
backfill or compatibility mechanism. Those are implementation-gate questions.
The contract is the semantic source identity the later design must represent.

### 5. Confirmation, warnings and terminal policy

Signed evidence binds practice, target, actor, opaque session digest, command,
state version, warning codes and freshness identifier. It is checked against
the locked recomputation. Confirmation remains distinct from freshness: a
fresh state does not imply human confirmation and old confirmation cannot make
a changed state fresh.

Submitted warning codes must equal the canonical current warning set. Missing,
extra, duplicate or unknown codes stop as `confirmation_required`. A terminal
appointment requested to move to a different status stops effect-free as
`transition_policy_deferred`; this architecture invents no product transition
policy.

### 6. Atomic write set and private correlation

Only `committed` may produce the three-member write set:

- appointment mutation;
- attributable audit; and
- completed receipt.

The private completed receipt binds operation, practice, target, actor, opaque
session digest, idempotency key, request digest, audit identifier, pre/post
state versions and public response digest. The three members commit or roll
back together. Public response compatibility does not require exposing the
private audit or session correlation fields.

### 7. Stored canonical delivery

The completed receipt owns canonical public response bytes over the current
appointment response fields. Initial success and same-digest replay both render
those exact stored bytes. They do not independently rebuild a response object.

If delivery fails after commit, the durable outcome is not rolled back or
retried by the server. Delivery becomes `delivery_unknown`; a client retry with
the same idempotency key and request digest re-enters the authority-first lock
boundary and returns the stored receipt without another effect.

## Scenario result

Twenty authored-synthetic scenarios cover clean commit, waiting-area
discrimination, incomplete authority, missing/mismatched sessions, missing
target, revoked authority, invalid evidence, stale version, four warning
mismatches, terminal deferral, same/different digest outcomes, response loss,
retry, and two rollback points. Only clean commit and the hypothetical
post-commit delivery-loss case have a complete atomic write set. Replay writes
nothing in the invocation and discloses only after current-authority checking.

All 56 hostile changes are rejected. They try to soften source hashes,
status-only discrimination, server ownership, lock order, source version,
evidence, warning equality, terminal deferral, audit/receipt correlation,
stored delivery, scenario effects and the unmounted handoff.

## What this resolves

The architecture closes all seven review blockers and both partial gaps at the
design level:

- ordered practice/appointment/idempotency locking;
- in-transaction current authority plus opaque session binding;
- status-only union discrimination;
- fail-closed terminal re-transition;
- exact warning acknowledgement;
- locked monotonic source-version evidence;
- atomic mutation/audit/receipt correlation;
- authority-first replay/conflict disclosure; and
- one stored canonical initial/replay delivery contract.

## Deliberately unproved

This document does not prove ORM/service feasibility, PostgreSQL lock behavior,
physical version storage, migrations/backfills, route parity, exception
mapping, transaction races, restart/unknown-commit behavior, waiting-area
regression safety or product policy. It grants no runtime or implementation.

No application source, database, provider, credential, browser authorization,
product/patient data, watcher, event transport, command, deployment,
production, release, Pages or protected ref was opened. `docs/branding/` and all
unrelated untracked files remain excluded.

## Next safe candidate

The next safe descendant is the provider-free unmounted status-confirm runtime
convergence rehearsal: a pure in-memory state machine over this exact contract.
It may prove schedule/rollback/disclosure behavior without importing a route or
database. Physical implementation remains closed.
