# Provider-free default-off runtime-instrumentation architecture plan

Date: 2026-08-12

Source HEAD: `42e3f9a6df86210be2e7a3709118ad53ba496e98`

Status: `frozen_for_source_bound_static_architecture_execution`

## Purpose

Freeze the narrowest feasible mounting architecture for the accepted shadow
comparison beside the four raw appointment routes. This tranche may inspect and
bind the current application source, but it edits and executes none of it and
creates no runtime component.

## Source finding that controls the design

All four raw routes live in `app/routers/appointments.py` and call commit-owning
helpers:

- create directly returns `_create_appointment_from_body(...)`;
- update directly returns `_apply_appointment_update(...)`;
- status directly returns `_apply_appointment_status_update(...)`; and
- delete calls `_apply_appointment_delete(...)` then implicitly returns the
  declared HTTP 204 result.

The helper success boundary is after mutation, audit and `db.commit()`, but it
is before FastAPI has serialized or sent the response body. Therefore a route-
local observer call cannot honestly satisfy the accepted sealed-response rule.
The architecture must use two phases: route-local staging after helper success,
then one-way handoff only after the final ASGI response-body frame has first
been sent successfully.

## Frozen two-phase architecture

### Phase 1 — route-local staging

After the command helper returns successfully and before the route returns:

1. read an immutable process-start generation snapshot;
2. short-circuit unless global enablement is exactly `enabled`;
3. require current generation, practice digest allowlisting, exact route
   allowlisting and no external disable latch;
4. require a server-minted correlation reference and authenticated server-side
   session reference;
5. build only the accepted 24-field digest projection through a dedicated
   versioned HMAC port; and
6. place that immutable projection in a request-scoped single-assignment cell.

The route stage invokes no adapter, observer or sink and receives no return
value from them. Any missing context, admission denial or staging failure leaves
the cell empty and immediately returns the already completed logical primary
result.

### Phase 2 — post-response handoff

One pure ASGI middleware mounted outside the existing user middleware stack may
observe message ordering only. It must:

1. await the original `send(message)` first;
2. act only after a successful final `http.response.body` frame with
   `more_body` false;
3. atomically take and clear the single staged projection;
4. call one bounded `offer_nowait(projection)` port with no `await`, retry or
   result channel; and
5. contain offer failure after the response is already sent.

The handoff port receives neither `send`, request/response bodies, headers,
database/session objects, models, users nor command services.

## Configuration and identity boundary

The shadow generation is distinct from `appointment_raw_compat_mode`. It is
immutable and process-start validated. Global and practice controls default to
disabled, the route allowlist defaults empty, and a separate external latch can
only disable. The generation contains a digest-key reference/version, never key
material. No database, feature service or network lookup is permitted.

The request context must be server-owned. Hashing a bearer token, treating an
inbound correlation header as authoritative, inventing a session binding or
falling back to a direct identifier is forbidden. The current raw routes expose
neither `Request` nor a safe general session/correlation dependency; this is a
recorded implementation prerequisite, not a reason to weaken the projection.

## Data minimization

The future projection factory may receive raw values only after all admission
controls pass. It must immediately return the exact accepted 24 fields and may
not retain inputs. Free-text fields and response material are never inputs.
`request_shape_digest` is derived from an allowlisted field-name/type shape;
`command_digest` is derived only from allowlisted non-free-text structural
command values. A diagnostic record remains the accepted 15-field lossy shape.

## Owned files

- this plan;
- `docs/raisa-provider-free-default-off-runtime-instrumentation-architecture.md`;
- `docs/security/raisa-provider-free-default-off-runtime-instrumentation-architecture-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-default-off-runtime-instrumentation-architecture/contract.json`;
- its closed schema;
- `scripts/raisa_provider_free_default_off_runtime_instrumentation_architecture.py`;
- `tests/test_raisa_provider_free_default_off_runtime_instrumentation_architecture.py`;
- the preplanning receipt pair; and
- exact closeout, acceptance, Yuri mailbox, Continuity/Compass updater and
  lifecycle artifacts if the tranche passes.

## Forbidden surfaces

- no edit, import, execution, wrapping or instrumentation of an application
  route, middleware, dependency, setting or test fixture;
- no FastAPI, ASGI or PostgreSQL process;
- no runtime hook, feature flag, thread, process, queue, sink, persistence,
  retention or aggregation;
- no database, source, watcher, event, provider or network access;
- no credential, IAM, metadata or digest-key access;
- no product-derived, patient, person, clinical, financial or free-text data;
- no kernel invocation, executable product tool, command, write or mutation;
- no client/header behavior change, deployment, production, release, Pages
  rebuild or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated untracked
  file.

## Acceptance

The tranche passes only when:

1. one closed schema validates one exact source-hashed architecture contract;
2. AST/source evidence binds exactly the four raw route handlers, decorators,
   command helpers, commit-before-return helper facts and current return forms;
3. the contract states that route-local success seals transaction/audit and the
   logical result, but not serialized response bytes;
4. the two-phase stage/after-send order is exact and handoff occurs only after
   the original final response-body send succeeds;
5. configuration is immutable, distinct from raw-compat mode, defaults deny and
   permits external disable only;
6. missing safe server session/correlation context denies observation and token
   hashing, inbound correlation trust and identity fallback are forbidden;
7. the projection/record field sets remain exactly 24/15 and free text,
   response material, direct identifiers, tokens and credentials are excluded;
8. route staging cannot import/call observer, adapter or sink, while the
   post-send handoff port cannot receive response, route, database or command
   capabilities;
9. every response/transaction/audit/command/client feedback edge remains
   forbidden;
10. at least forty independent hostile architecture mutations fail closed;
11. focused API Spine, route-source, parent, canonical repository-profile and
    Git whitespace checks pass; and
12. protected refs and every pre-existing untracked file remain unchanged.

## Recovery and next work

One bounded mechanical correction may repair a schema, source hash, AST fact,
validator or assertion without changing two-phase ordering, default denial,
identity provenance, minimization or no-feedback rules. Any proposal to observe
before commit, hand off before final send, hash a bearer token, trust an inbound
correlation identifier, read a database feature flag, expose response material
or invoke a command is conceptual and stops this tranche.

After acceptance, the next safe candidate is a provider-free default-off
instrumentation scaffold. It would implement only the typed generation,
request-cell, projection and post-send interfaces plus globally disabled wiring,
then prove byte-for-byte route parity with authored-synthetic local tests. It
would still grant no enabled practice, operational diagnostic sink, patient data
retention, kernel convergence, deployment or production authority.
