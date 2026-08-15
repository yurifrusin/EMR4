# Delete-confirm conditional-command kernel architecture and admission

Date: 2026-08-15

Timestamp: 2026-08-15T12:56:41+10:00 (Australia/Brisbane)

Status: accepted; development continuing

## Lay summary

The cancellation foundation now passes as a complete abstract contract. Raisa
must make the final decision against locked appointment truth and the staff
member's current authority, then commit the cancellation, audit and receipt as
one indivisible result. Stale, revoked, duplicate, conflicting and interrupted
requests all stop safely or return the one original result.

This is the point at which cancellation has a precise kernel of truth, but it
is deliberately still off the product surface. We have not changed the live
route, database or Reception One interface. The next step is to prove that the
design can be represented honestly in the repository's real PostgreSQL and
application structures.

## Technical summary

At reviewed source `356b28a1750e7a7b379406e864f2a3501606938a`:

- 46 decision cases and 15 transaction schedules pass;
- all 67 hostile mutations fail closed;
- the exact lock order is `practice -> appointment -> idempotency_record`;
- current authority is checked twice inside the locked transaction;
- one exact 24-field signed-evidence contract binds identity, target, pre-state,
  reasons, warnings, freshness and request digest;
- structured and nullable free-text cancellation reasons remain identical in
  appointment, audit and receipt;
- rollback and unknown-delivery replay preserve exactly-once effects; and
- readback is separately authorised and never masquerades as transaction proof.

DeepSeek's first scaffold exposed a conceptual self-pass error and was not
accepted. Sol recovered it under the recorded lease, and Gemini then passed all
15 independent challenges at an unchanged clean candidate. Focused, combined,
register and canonical checks all pass.

The required non-PHI continuing closeout notification succeeded with request
`1c7333ac-0017-4945-ae1d-37d8cdf017e1` and status `1`.

## What Raisa is becoming

The architecture now has a clear natural seam. Raisa is the typed,
authority-bearing kernel; Reception One is the first-party native reference
client. Later email, SMS, WhatsApp, thin-browser, Siri/Alexa or general-chatbot
interfaces can be separately authorised adapters that present projections and
relay human intent, but they cannot invent truth, reinterpret required
semantics or acquire command authority.

This matters for delivery. The first production release can concentrate on a
reliable core Raisa kernel and an excellent native Reception One client instead
of waiting until every possible channel has been built. Later clients can be
added against the stable versioned seam, each behind its own identity,
delegation, privacy, replay and conformance gate.

The same architecture can carry into Clinician One. Its Word/Office workspace
becomes the first-party clinical reference client, while the backend retains
patient/encounter truth, permissions, versioning, clinician attestation, audit
and final commit. Dictation, another editor or another authorised clinical
surface could come later without inheriting clinician authority merely because
it can speak the protocol.

My Health Record also fits the wider adapter architecture, but as a regulated
integration adapter rather than a UI. Outbound it translates an authorised
slice of Raisa truth; inbound it yields source-labelled external evidence, not
automatic local truth. Submission or amendment remains an explicit authorised,
audited command with readback. The existing later ADHA/IHI/MHR/AIR programme
gate is unchanged.

This broadens the ultimate proposition: EMR4 may become a provider-agnostic,
provider-qualified meta-harness for safe contemporary machine intelligence in
general practice. Models can change behind stable Bureau contracts while the
deterministic system retains truth, authority, proofreading, human/clinician
gates, commands, audit, receipts and revocation. “Provider-accredited” remains
reserved until a genuine accreditation scheme and regulatory meaning exist;
no present safety or certification claim is made.

The durable direction note is
`docs/raisa-authority-kernel-reference-client-adapter-seam.md`.

## Deliberately closed

No route, OpenAPI, GraphQL, database, migration, watcher, event runtime,
Reception One UI, external patient client, channel adapter, provider,
patient/product/clinical data, credential/IAM, command/write, deployment,
production, release, Pages or protected ref changed. The ordinary raw delete
and status fallback remain separate and are not approved for Reception One.

## Next

Development is continuing into the provider-free unmounted delete-confirm
physical representability review. It will remain read-only with respect to
mounted product behavior. Yuri attention is not required.

Formal closeout:
`docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-closeout.md`.
