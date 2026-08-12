# Globally-disabled runtime instrumentation - lay and technical closeout

Date: 2026-08-12

Result: `passed`

## Lay summary

The safe mounting frame designed in the previous tranche is now present in the
application, but it is bolted shut. The system knows the shapes of a tiny
single-use note, a private request slot and an after-response handoff, yet the
only allowed setting is off everywhere. It has no observer to receive anything
and no secret key with which to create identity digests.

The four older appointment write routes now touch this frame only after their
ordinary database-and-audit work succeeds. Because the frame is off, the touch
immediately returns: it does not inspect the user or appointment, construct a
note, allocate the private slot, wrap the HTTP response or attempt a handoff.
The appointment result is unchanged.

## Technical summary

- accepted source: `410ea6dbbe28b94cfaa83ac5f6b586910c77aa6a`;
- immutable generation rejects enabled, allowlisted, key-bearing and stale
  states;
- route staging is post-helper and takes only one closed adapter constant;
- the disabled stage performs zero context, projection, digest or cell work;
- outer ASGI middleware delegates directly and makes zero offers while disabled;
- the cell and future finalizer shapes prove single assignment, take-and-clear,
  final-send-before-offer and contained failure;
- authored-synthetic create/update/status/delete retain exact status, response,
  headers, database truth and audit attribution;
- auth, validation, conflict and helper failures do not stage, while a later
  serialization failure still cannot emit an offer;
- 17 tranche tests, 170 focused tests, the canonical 191-test profile, Ruff,
  204 maintained sources, Diary JavaScript and whitespace all pass; and
- Continuity 252 / Compass 234 is current.

## Deliberately closed

There is no enabled practice or route, context provider, digest key, observer,
adapter invocation, sink, queue, persistence, operational database/source/
watcher/event/provider access, product or patient data, kernel, new command,
deployment, release, Pages or protected-ref movement. All pre-existing untracked
files, including `docs/branding/`, remain preserved and excluded.

## Next tranche

The next work examines the Diary client rather than enabling the shadow. It
will inventory every ordinary or fallback path still capable of calling the raw
create/update/status/delete endpoints, then prove the proposal-and-confirm path
can replace each one without losing ordinary behavior or emergency fallback.
The compatibility routes remain available during that proof. Yuri's attention
is not required; this continues under standing authority.
