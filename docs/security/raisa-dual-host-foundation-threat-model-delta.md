# Threat-model delta: Raisa candidate dual-host foundation

Date: 2026-07-31

Status: `active_provider_free_development`

Parent boundaries:

- Reception One Word Hybrid contextual launch;
- Reception One compact companion shell;
- supervised Word desktop dialog check;
- platform-blocked Word Online localhost check; and
- EMR4 API Spine and Access AI boundaries.

## New surface

A pure JavaScript runtime observes the presence of Office, Word and browser
capabilities and publishes one immutable host profile to the existing Word
taskpane.

It adds no API call, message type, provider adapter, backend route, document
operation, microphone operation or product entitlement.

## Threats and controls

### Capability is confused with authority

Threat: `host_ready` is interpreted as permission to read a document, capture
audio, call a provider or perform a command.

Controls:

- every feature decision is labelled `host_capability_only`;
- product authorization is explicitly `not_evaluated`;
- the profile carries false document, microphone, network, provider, context,
  command and write authority; and
- the runtime exposes no operation that invokes a capability.

### Host spoofing opens a feature

Threat: a crafted platform string claims to be desktop or web and bypasses
actual capability checks.

Controls:

- feature readiness derives from observed API presence, not platform name;
- platform is a display/strategy enum only;
- unknown values normalize to `unknown`; and
- missing APIs produce exact closed reason codes.

### Capability probing reads sensitive state

Threat: host detection inspects document content, account identity,
credentials, storage, URLs, microphone state or backend configuration.

Controls:

- the dependency-injected constructor checks only function/object presence;
- it does not call Office, Word, browser media, storage, crypto, network or
  document APIs;
- deterministic Node tests use inert authored fixtures; and
- the profile contains no identifier, token, URL or free-text field.

### Word Online differences are hidden by a desktop pass

Threat: the existing desktop acceptance is treated as evidence that Word
Online, microphone permissions or cross-origin dialogs work.

Controls:

- evidence status is recorded per host and per feature;
- the Word Online localhost result remains platform-blocked before taskpane
  code;
- the profile test matrix is labelled deterministic fixture evidence; and
- public HTTPS Word Online and microphone checks remain future gates.

### Candidate branding rewrites programme history

Threat: candidate Raisa or Clinician One naming changes manifests, historical
nodes, accepted result identifiers or trade-mark posture.

Controls:

- candidate names appear only in the new plan, inventory and descendant;
- EMR4 remains the internal technical identity;
- historical nodes are not revised; and
- public rename, artwork, registration, domain and trade-mark actions remain
  closed.

### Scribe capability leaks directly to a provider

Threat: identifying media capability is used to call the existing
`/scribe-consultation` or `/analyze-consultation` paths.

Controls:

- the host runtime contains no URL, fetch, request or provider code;
- voice capture and Access AI invocation remain separately gated;
- frontend surfaces must continue to call EMR4 rather than a provider; and
- provider, clinical-context and write authority remain false.

### Patient reception becomes a separate source of truth

Threat: online booking, Rayleen or a third-party booking product evolves into a
parallel reception system with different availability, identity, appointment
or arrival truth.

Controls:

- Reception One remains one backend-owned reception domain;
- staff, clinician and future patient clients receive role-scoped contracts
  over the same authoritative services;
- future online-booking and Rayleen writes must use explicit patient-facing
  commands with identity proofing, tenancy, idempotency and audit;
- external integrations, if later approved, remain subordinate adapters; and
- this increment opens no external-patient client, arrival or booking write.

### Cloud-first becomes implicit multi-tenant trust

Threat: describing the system as cloud-first is mistaken for authority to
deploy, pool practice data, weaken residency or make a local edge a second
clinical or reception system.

Controls:

- cloud-first is a delivery direction, not present infrastructure authority;
- every future service remains practice-scoped with explicit identity,
  tenancy, audit, residency, recovery and command controls;
- no cloud resource, deployment, billing or production state changes here;
- any later local-model or on-premises component is a subordinate edge behind
  typed contracts and cannot own parallel patient, appointment, arrival,
  clinical or audit truth; and
- provider and data admission remain separately gated.

## Preserved API Spine controls

- GraphQL remains read-only.
- Clinical or scheduling writes remain explicit, practice-scoped, auditable
  REST commands with the required human confirmation.
- Frontends do not call AI providers directly.
- Product entitlement remains separate from infrastructure and host
  capability.
- The native Diary remains authoritative for scheduling detail.

## Candid residual risk

Static API presence does not prove that a permission will be granted, that a
browser/tenant permits dialogs, that audio codecs behave consistently, or that
Word document APIs have matching semantics on every platform. Those require
separate supervised host exercises with authored-synthetic data and their own
data, provider and deployment authority.
