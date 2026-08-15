# Raisa authority-kernel and reference-client adapter seam

Date: 2026-08-15

Timestamp: 2026-08-15T12:56:41+10:00 (Australia/Brisbane)

Status: `recorded_architectural_direction_no_new_runtime_authority`

## Direction

Raisa is developing into an authority-bearing protocol and deterministic
backend kernel with replaceable human-facing adapters. `RECEPTION ONE™` is the
first-party native reference client for that protocol, not the only possible
way a person may eventually interact with Raisa.

The durable seam is therefore:

1. a backend-owned authority kernel that owns identity and delegation checks,
   current source truth, typed projections, freshness, proposal evidence,
   confirmation rules, idempotency, transaction effects, audit and receipts;
2. a versioned API protocol that exposes only the typed facts, affordances and
   command envelopes an authorised interaction needs; and
3. one or more adapters that render those projections and collect intent or
   confirmation without acquiring authority of their own.

## Reference-client rule

Reception One should be the first and strongest conformance client. It proves
that Raisa's native desktop/tablet interaction can display current truth,
collect explicit human choices and reconcile committed outcomes without a
second command path. Its implementation may be richer than later thin clients,
but its authority must not be richer.

A future email, SMS, WhatsApp, thin-web, voice-assistant or general-chatbot
adapter may choose different words and controls. It may submit typed intent,
render an intent-shaped projection, collect a human response and relay a
backend-issued challenge. It may not invent availability, reinterpret a
required warning, self-confirm, confer identity or delegation, treat an event
as current truth, or perform a write outside the canonical command plane.

## Protocol evolution

Clients should receive a contract/version identifier, typed response shape,
required capability indicators, freshness and confirmation evidence, and a
deterministic unsupported-version outcome. The complete schema need not be
retransmitted with every response: it may be distributed as a signed or
source-controlled machine-readable contract, while each exchange carries the
exact version and required semantics that bind it.

Unknown required fields, unsupported contract versions or missing mandatory
capabilities fail closed. Backward compatibility belongs in explicit server
adapters or versioned routes; it must not be guessed by a model or presentation
client.

## Parallel application to Clinician One

The same seam should govern `Clinician One`. Its Word/Office workspace is the
first-party reference client for clinical work, while authoritative backend
services own patient and encounter identity, current record truth, role and
purpose checks, document versions, clinician attestation, validation, audit and
final commit. Model-generated or dictated content remains a provisional draft
until an authenticated clinician reviews and signs the exact version.

A later clinical editor, tablet surface, dictation client or authorised
specialist workflow may use the same typed clinical protocol. No adapter may
infer clinician identity, authorship, consent or legal attestation from device,
channel or model context. Those properties require explicit backend-verifiable
evidence at the clinical command boundary.

## Regulated integration adapters

My Health Record is a likely EMR4-owned adapter, but it belongs to a stricter
regulated-integration class rather than the human-facing client class. Outbound,
it may translate an explicitly selected and authorised slice of current Raisa
clinical truth into the required My Health Record document or API vocabulary,
preserving patient identity, consent, clinician authorship and provenance.
Inbound, it may translate My Health Record material into typed, source-labelled
external evidence; it must not silently promote an external document to local
clinical truth.

Upload, amendment, withdrawal and other external effects remain explicit,
idempotent, audited backend commands with current organisational and clinician
authority plus external readback. The repository's existing Phase 10
ADHA/IHI/MHR/AIR gate remains unchanged; exact standards, accreditation,
credentials and production integration must be reviewed at that later gate.

## Production consequence

The first production horizon need not include every possible patient, staff or
clinical application. EMR4 can concentrate on making the authority kernels and
native Reception One and Clinician One reference clients safe, reliable and
useful, while keeping their typed seams stable enough for later adapters. This
shortens the breadth of the first release without weakening its correctness
boundary and avoids duplicating business rules for every future channel.

That does not make later channels automatically safe or cheap. Each adapter
still needs a separately reviewed identity, account binding, revocable
delegation, consent, anti-replay, privacy, rate-limit, recovery, presentation
and conformance gate appropriate to its medium.

## Higher-order product proposition

Taken together, these seams make EMR4 a candidate general-practice
medical-management intelligence meta-harness. Model providers contribute
bounded interpretation, synthesis and dialogue behind stable Bureau contracts;
deterministic services retain evidence admission, current truth, authority,
proofreading, human or clinician gates, commands, audit, receipts, revocation
and degraded-operation behavior.

The harness should remain provider-agnostic but provider-qualified. A model or
provider is admitted only against a versioned task-specific evidence profile
covering capability, typed-output conformance, privacy and location posture,
cost/budget, failure behavior and ongoing monitoring. Provider identity alone
never grants trust, no silent fallback is allowed, and `intelligence_unavailable`
is preferable to weakening the deterministic boundary.

`Provider-qualified` or `provider-admitted` is the current architectural term.
`Provider-accredited` is reserved until EMR4 defines a formal accreditation
owner, criteria, lifecycle and relationship to Australian health, privacy and
medical-device obligations. This document makes no present safety,
certification, accreditation or production-readiness claim.

## Closed gates

This direction creates no external patient client, email/SMS/WhatsApp or voice
runtime, chatbot registration, alternate clinical editor, dictation runtime,
My Health Record connection, identity provider, delegation grant, route,
database access, provider call, deployment or production exposure. It does not
authorise arbitrary clients or allow clients to carry backend or clinician
authority. Those remain future programme gates.
