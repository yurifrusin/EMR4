# Provider-free globally-disabled runtime-instrumentation scaffold design

Date: 2026-08-12

Status: `frozen_bounded_design`

## Safety argument

This scaffold deliberately implements shapes and placement without implementing
enablement. `ShadowInstrumentationGeneration` rejects enabled state, non-empty
allowlists and a digest-key reference. Consequently both application entry
points short-circuit on the first generation check:

- the route stage reads no request context or command material; and
- the ASGI middleware delegates to the existing stack without creating a cell,
  wrapping `send` or contacting an offer port.

The route-stage call itself carries only one closed adapter identity. It cannot
receive a request body, user, database session, response or direct identifier.

## Route transformation

Create, update and status change from `return helper(...)` to:

```text
result = helper(...)
shadow_runtime.try_stage("exact_adapter_id")
return result
```

Delete remains:

```text
helper(...)
shadow_runtime.try_stage("raw_compat_delete")
<implicit None>
```

The helper remains sole owner of mutation, audit, commit and returned domain
state. Authentication, validation and helper exceptions skip staging. The
ignored stage result is `None`; there is no feedback channel.

## Future-shaped but closed interfaces

The context and digest ports exist only as protocols. The exact projection
factory can be proved with authored-synthetic structural input, but the runtime
has neither a context provider nor a digest implementation and therefore cannot
call it. The offer port has one synchronous `offer_nowait` method returning
`None`; the only application implementation rejects direct use.

The request cell uses a context-local binding only inside the admitted
middleware branch. It rejects a second store permanently, and `take()` clears
the value so a second final-body observation returns no projection.

## No claim expansion

This is application wiring, but it is dormant wiring. It does not observe a
request, create a diagnostic record or prove operational performance. A later
enablement proposal must add a new reviewed generation type, safe server-owned
context creation, digest-key custody, budgets, observer isolation and an exact
practice/route admission plan; none is latent authority from this scaffold.
