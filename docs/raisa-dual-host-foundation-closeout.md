# Raisa candidate dual-host foundation closeout

Date: 2026-07-31

Result: `raisa_dual_host_foundation_pass`

## Outcome

The existing Word add-in now has one shared, host-neutral capability layer for
the clinician and Reception One surfaces. It classifies Word desktop, Word
Online, mobile Word and unknown fixtures, produces a deeply immutable profile,
and keeps technical readiness separate from authentication, role, data and
action authority.

The runtime loads before the existing taskpane in both source and published
copies. `Office.onReady` publishes the frozen profile for local diagnostics.
The profile constructor invokes none of the capability objects it observes and
grants no document, microphone, network, provider, patient, clinical, command
or write authority.

The durable inventory now includes the earlier clinician taskpane and medical
scribe work as well as the newer Reception One dialog and compact companion.
Legacy direct-backend clinical and scribe paths are recorded as migration work,
not silently treated as dual-host-ready.

## Integrated reception direction

Reception One is recorded as one backend-owned reception domain with
role-scoped surfaces:

- reception staff receive the full authorised workflow;
- doctors receive clinician-appropriate reception views and coordination;
- a future online-booking client receives only its patient booking contract;
- a future Rayleen client receives only its patient arrival contract.

Those surfaces must share identity, availability, appointment, arrival, audit
and event truth. A third-party booking or arrival product is not selected as
the primary patient surface or a parallel source of truth. Future external
integrations, if any, remain subordinate typed adapters.

This records product direction only. It grants no online-booking, Rayleen,
patient-identity, arrival-write or external-patient authority.

The wider candidate Raisa delivery direction is cloud-first practice
management as a service, so Word desktop, Word Online, the native Diary and
future patient surfaces can share practice-scoped contracts without extensive
local setup. A future on-premises or local-model component may be a subordinate
privacy/latency edge, but not a second clinical, reception or audit system.
This records architecture direction only and created no cloud resource,
tenancy, deployment, billing or production state.

## Verification

- Host-profile schema and deterministic desktop/web/mobile/unknown fixtures:
  passed.
- Capability invocation count: zero.
- Deep immutability and fail-closed capability decisions: passed.
- Source/published runtime and taskpane parity: passed.
- Focused Raisa, Hybrid, compact companion, Word desktop, Word Online and API
  Spine tests: passed.
- Webpack development build and JavaScript syntax: passed.
- Local ordinary-browser rendering at the taskpane route: passed without
  console errors or an error overlay.
- Task-owned browser tab, listener, processes, containers, networks, images
  and temporary logs: absent after cleanup.

## Evidence boundary

This proves a repository-local host-capability contract and its integration
with the current taskpane. It does not prove authenticated Word Online
execution, microphone behavior, scribe correctness, clinician workflow safety,
live backend or provider authorization, real or product-derived data safety,
patient-facing online booking, Rayleen registration, production deployment,
public naming or release readiness.

Raisa and Clinician One remain candidate names. EMR4 remains the repository and
technical identity.

## Recommended next descendant

Move the first clinician operation behind the shared foundation as a
provider-free, typed, read-only document-context adapter, with separate desktop
and web host evidence. A real Word Online check still requires an authorised
non-loopback HTTPS development host or a platform-policy change; the localhost
gate must not be weakened.
