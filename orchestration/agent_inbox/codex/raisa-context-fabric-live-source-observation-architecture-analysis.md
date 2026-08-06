# Independent architecture challenge: live-source observation boundary

Date: 2026-08-06

Reviewer: fresh native Sol/xhigh read-only analysis lane

Reviewed source: `cead332c43afccafed4d0c3ef00ef0e1f36f0869`

Decision: no Yuri-owned material fork; freeze the transport-neutral
architecture after the hardening below.

## Classification

The tranche is an architecture-only internal async observation-admission
boundary. It is neither a GraphQL read surface nor a REST/OpenAPI command and
adds no subscription, route, source reader, watcher, database consumer,
persistence, provider integration or runtime wiring.

The authority path is:

`authenticated source metadata`
-> strict admission and minimisation
-> accepted payload-free `TemporalSignalEnvelope`
-> accepted temporal invalidation classifier
-> inert `ContextReassemblyRequirement`
-> fresh application-principal authority check
-> new no-wider `ContextNeed` and `ContextScopeGrant`
-> future separately authorised source read.

The observer may cause a read to be considered. It never authorises, performs,
receives or returns that read.

## Required hardening

- Disabled means no connection, credential acquisition, admission, cursor
  movement or read request.
- Policy and binding allow no wildcard practice, source, event, schema,
  aggregate or selector scope and fix payload, returned-data, read, provider,
  command and persistence authority false.
- Payload-free does not mean merely no patient name. Patient/person,
  practitioner, location, appointment-time, free-text, before/after, callback,
  credential, provider and command material are prohibited; event-supplied
  dependency lists are not trusted.
- The backend constructs the accepted `TemporalSignalEnvelope`; the sealed
  manifest determines impact. Unknown impact blocks or causes bounded full
  invalidation.
- Continuity requires a monotonic transaction/outbox coordinate. The existing
  Diary feed's `(occurred_at, event_id)` cursor cannot support a no-loss claim
  and must not be inherited as this boundary.
- Exactly one pending requirement exists per affected frame generation; later
  relevant observations coalesce without a read storm or authority renewal.
- Same-packet proofreading reconstructs provenance from authoritative inputs
  and rejects self-consistently resealed substitutions.
- No acknowledgement, durable checkpoint, retention, retry or crash-recovery
  claim is made in this architecture tranche.

## Deferred implementation choice

The exact first source/event family, transport principal and durable monotonic
coordinate remain deliberately closed. A later source-specific descendant must
choose one exact schema and position mechanism, or explicitly accept weaker
delivery evidence, before any feed, listener, persistence, checkpoint or
product read is authorised.

No edits, provider calls, product/patient data, runtime actions, command,
deployment, Pages operation or protected-ref movement occurred in the analysis
lane.
