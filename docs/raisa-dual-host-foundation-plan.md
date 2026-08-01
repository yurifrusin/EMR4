# Raisa candidate dual-host foundation plan

Date: 2026-07-31

Owner: Yuri / GPT Sol

Status: `authorised_provider_free_development`

## 1. Authority and product direction

Yuri authorised the first dual-host foundation after confirming that the Word
architecture must include both the earlier clinician taskpane and medical
scribe work and the newer Reception One companion.

The candidate product hierarchy for this increment is:

- `Raisa` as a candidate master brand;
- `Clinician One` as a candidate name for the clinician workspace;
- `Reception One` as the existing provisional reception workspace; and
- `EMR4` as the unchanged internal repository and technical identity.

These are candidate names only. This increment does not publicly rename the
application, manifest, repository, historical evidence or user interface. It
performs no ASIC, domain, artwork or trade-mark action.

### Integrated Reception One invariant

Reception One is one reception domain presented through role-scoped surfaces,
not a collection of disconnected products:

- reception staff receive the full authorised Diary and reception workflow;
- doctors receive the smaller clinician-facing view and coordination actions
  appropriate to their role;
- a future online-booking surface receives only the patient-facing booking
  contract;
- a future Rayleen arrival-registration surface receives only the
  patient-facing arrival contract; and
- every surface converges on the same backend-owned identity, availability,
  appointment, arrival, audit and event truth.

A third-party booking or reception product must not become the primary patient
surface or a parallel source of reception truth merely for convenience. Any
future external integration is subordinate to typed EMR4 contracts and cannot
bypass Reception One's authority, audit or consistent interaction model.

This is a durable product direction, not current external-patient authority.
Online booking, patient identity proofing, Rayleen, arrival writes and external
patient clients remain separately gated.

### Cloud-first service invariant

The candidate Raisa system is cloud-first practice management as a service:

- a new practice should be able to establish its authorised workspace with
  minimal local infrastructure;
- Word desktop, Word Online, the native Diary, Reception One, future online
  booking and future Rayleen clients converge on the same cloud-owned
  practice-scoped contracts and truth;
- tenancy, identity, audit, data residency, availability and recovery remain
  explicit platform controls rather than per-device assumptions; and
- a future on-premises or local-model capability may be a subordinate
  privacy/latency edge, but must not create a parallel patient, appointment,
  arrival, clinical or audit record.

This is architecture direction only. It creates no cloud resource, tenancy,
deployment, production, billing, domain, patient-data or local-model authority.

## 2. Objective

Create the first shared, host-neutral Office runtime contract used by the
existing Word taskpane. It must:

1. distinguish Word desktop, Word Online, mobile Word and unknown hosts;
2. observe only the presence of exact technical capabilities needed by the
   clinician and reception surfaces;
3. produce one closed, immutable host profile;
4. identify host readiness separately from product authorization;
5. load before the existing taskpane application in both source and published
   copies; and
6. integrate with `Office.onReady` without changing the accepted Reception One
   exchange or activating clinical scribe, provider, backend or write paths.

## 3. Boundary classification

This is an Office client capability-manifest change under the API Spine. It is
not:

- a GraphQL read;
- a REST command;
- a provider invocation;
- a clinical-context read;
- a document-content read or write;
- a microphone capture;
- an authentication or entitlement decision; or
- a public product rename.

The runtime may inspect only whether the following APIs are present:

- Word JavaScript runtime;
- Office Dialog API;
- Office action association;
- Custom XML parts;
- browser media devices;
- `MediaRecorder`;
- Office device-permission API; and
- cryptographic random UUID support.

It must not call those APIs while constructing the profile.

## 4. Frozen host profile

The exact profile is
`emr4.office-host-runtime-profile.v1`. It contains:

- normalized platform and host-kind enums;
- a closed capability boolean map;
- a host-specific microphone-permission strategy label;
- four host-readiness decisions:
  - `clinician_one.workspace`;
  - `clinician_one.scribe_capture`;
  - `reception_one.dialog`;
  - `reception_one.companion`;
- missing-capability reason codes; and
- explicit false authority flags for document access, microphone capture,
  network access, provider invocation, clinical or patient context, commands
  and writes.

`host_ready` means only that the host exposes the prerequisites. It never means
that a user, practice, role, backend, provider or data class has authorized the
feature.

## 5. Existing feature inventory

The durable inventory must cover at least:

- clinician patient-file detection and context;
- consultation start and bounded note extraction;
- background consultation analysis;
- audio capture and scribe submission;
- clinician review/finalisation;
- ordinary Diary launch;
- Reception One contextual launch;
- Reception One compact request and proofreader-admitted summary; and
- desktop and Word Online evidence status.

For every item it must distinguish source presence, host prerequisite,
application authority and actual evidence. Existing desktop evidence may be
referenced but not reclassified. The Word Online localhost attempt remains
platform-blocked before taskpane execution.

## 6. Acceptance gates

### Gate A - rehydration and preservation

- Read `AGENTS.md` completely and restore sections 5 and 6.
- Read the active Hybrid, compact-companion, desktop, Word Online and API Spine
  materials.
- Verify HEAD, master, handoff/current and both origin refs.
- Preserve every unrelated worktree change.
- Produce a passing Ariadne receipt naming all five mandatory sources.

### Gate B - pure runtime contract

- The runtime is dependency-injected and testable outside Office.
- Profile creation performs no document, storage, network, microphone,
  credential or provider operation.
- Unknown host values fail to `unknown`; missing capabilities fail closed.
- The profile is deeply immutable.
- Every feature result says `host_capability_only` and
  `product_authorization_not_evaluated`.

### Gate C - both product surfaces

- Clinician One workspace readiness requires the Word runtime.
- Clinician One scribe-capture readiness additionally requires browser audio
  capture and `MediaRecorder`.
- Reception One dialog readiness requires the Office Dialog API.
- Reception One companion readiness requires the Dialog API and cryptographic
  request identifiers.
- The host runtime does not invoke the scribe, Access AI, Reception One
  planner, backend or any command.

### Gate D - source and published integration

- The runtime loads before `taskpane.js`.
- `Office.onReady` publishes one frozen profile for diagnostics.
- A technically unavailable scribe-capture button fails closed with
  receptionist/clinician-readable copy.
- Existing login, patient, clinician, Reception One and companion behavior is
  otherwise unchanged.
- Source and published taskpane runtime copies are identical.

### Gate E - verification

- Validate the profile JSON schema.
- Run deterministic desktop, web, mobile and unknown-host contract cases.
- Run the compact-companion, desktop-host and Hybrid focused tests.
- Run relevant API Spine and Compass checks.
- Run JavaScript syntax/build checks, Python compilation, JSON/schema
  validation and `git diff --check`.
- Check for task-owned process, listener, container and browser residue.

## 7. Closed boundaries

No provider call, ADC or API-key access, microphone capture, audio retention,
document-content access, patient or clinical context, backend or database
access, appointment command, clinical finalisation, write, production,
deployment, release, public rename, domain purchase, ASIC registration,
artwork publication or trade-mark action is authorised.

There is no microphone capture and no document-content read or write in this
increment; the runtime observes only whether capability objects are present.

No online-booking client, Rayleen client, arrival workflow or third-party
booking service is implemented or connected by this increment.

Protected holdouts, historical Diary material and real or product-derived
patient, health or clinical data remain unopened and unused.

## 8. Candid evidence limit

A pass proves only that one repository-local capability contract can classify
authored desktop/web/mobile/unknown Office host fixtures and initialize inside
the existing taskpane without opening a data or action path. It does not prove
an authenticated Word Online run, microphone behavior in either host, medical
scribe correctness, live backend or provider authorization, clinical safety,
production deployment, public branding or release readiness.
