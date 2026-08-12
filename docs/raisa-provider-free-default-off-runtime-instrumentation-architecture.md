# Provider-free default-off runtime-instrumentation architecture

Date: 2026-08-12

Status: `frozen_source_bound_static_architecture`

## Why the mounting seam is split

The current helper boundary is strong for database effects: each raw route's
helper owns audit and commit before success returns. It is not a serialized
response boundary. FastAPI converts the returned `AppointmentOut`—or the
delete route's implicit `None`—to HTTP messages after the handler returns.

Calling the observer inside the handler would therefore overclaim that the body
and headers were sealed. The route may only stage a projection. The observer
handoff belongs after the final ASGI body message has already passed through the
ordinary send function.

## Route seam map

| Adapter | Current handler result | Staging point |
|---|---|---|
| `raw_compat_create` | direct `AppointmentOut` helper return; declared 201 | helper success, before returning the local result |
| `raw_compat_update` | direct `AppointmentOut` helper return; default 200 | helper success, before returning the local result |
| `raw_compat_status` | direct `AppointmentOut` helper return; default 200 | helper success, before returning the local result |
| `raw_compat_delete` | helper call followed by implicit `None`; declared 204 | helper success, before the implicit return |

An exception from authentication, validation, conflict checking, mutation,
audit, commit, readback or serialization leaves the stage absent or prevents
the final-send trigger. It cannot produce a shadow record.

## Capability split

`ShadowRouteStage` may see only an immutable generation reader, a safe
server-owned request context, the exact route adapter identity, allowlisted
non-free-text command facts, a versioned digest port and a single-assignment
request cell. It has no observer, adapter, sink, database, transaction, response
writer, audit writer, event or kernel capability.

`ShadowAfterSendFinalizer` may see only the request cell and a bounded
`offer_nowait` port. Although its enclosing ASGI middleware observes message
ordering, the offer function is called after `send` and receives no send
callable or response content. It cannot await, retry or report a result to the
handler.

The later observer owns pure adapter/comparison behavior but is downstream of
the bounded handoff. It has no route, response, source or command capability.

## Context provenance

The current OAuth dependency proves actor and practice but exposes no safe
application-session or general request-correlation reference to these handlers.
The architecture refuses three tempting substitutions:

- hashing the bearer token;
- accepting a caller-supplied correlation value as authoritative; or
- inventing a session from actor/practice identity.

A future scaffold must supply server-created correlation and authenticated
server-side session references, or the stage denies observation. Direct
identifiers exist only transiently inside the admitted projection factory and
are released only as domain-separated HMAC digests.

## Configuration ownership

The generation snapshot is created and validated at process start. Any change
creates a new generation. It carries disabled/enabled labels, digest allowlists,
exact route allowlists, budgets and a digest-key reference; it carries no key or
direct practice identifier. Missing/unknown state denies. The external kill
latch is monotonic disable-only within the generation.

`appointment_raw_compat_mode` continues to control audit evidence and the
optional deprecation header only. It cannot enable, configure or disable shadow
instrumentation.

## Claim boundary

This design chooses contracts and proof obligations, not implementation code.
No route, middleware, dependency or setting has changed. The route line numbers
and hashes are evidence about the reviewed source only and are not durable API
identities; any source change requires a new architecture generation and static
review.
