# Threat-model delta: model-required Bureau A4 product read and UI

Date: 2026-08-05

Parent: `docs/security/emr4-model-required-bureau-a3-b3-request-contract-recovery-threat-model-delta.md`

## New trust crossings

1. An authenticated Reception One surface asks GraphQL for one minimized,
   practice/location-scoped waiting-room context and deterministic projection.
2. A separately default-off REST/Access-AI path may transform that same
   authored-synthetic frame to opaque references and send it to one isolated
   Vertex model cell.
3. A proofreader-admitted selector returns to the trusted backend and then to a
   read-only UI projection.

## Threats and required controls

| Threat | Required control |
|---|---|
| Cross-practice or foreign-location enumeration | Authenticate and authorize role/action/resource before data access; bind every query to current user practice; validate location ownership; generic denial. |
| Existing broad waiting-room response leaks PHI | New A4 service selects an explicit minimal column set and never serializes `AppointmentOut`, patient records, reason, notes, contact or national identifiers. |
| Missing arrival timestamp becomes a fabricated wait | Derive arrival from the latest committed Arrived audit only; emit `missing_arrival_timestamp` and no elapsed value when absent. |
| Client or model invents a selector | Closed projection enum; exact fresh revision; every appointment/practitioner/waiting-area reference must occur in the current frame; deterministic semantic proof. |
| GraphQL becomes a command/provider tunnel | Query root has no Mutation, write dependency, provider adapter or command bus. Provider invocation exists only in the separate REST/Access-AI boundary. |
| Model receives stable product identifiers or excess context | Request-scoped opaque HMAC references; newly authored synthetic practice only; bounded facts/signals; no raw identity, notes, clinical content, credential or whole Diary. |
| Prompt injection requests action or disclosure | Model is untrusted; no tools; all-false authority; hostile-byte parsing; closed schema; deterministic grounding/proofreading; no model text reaches UI. |
| Stale or out-of-order response replaces a fresh view | Revision and expiry binding plus client request generation/supersession; stale results render no cards and preserve ordinary fallback. |
| Ordinary Diary traffic escapes a local occupied-UI harness | Test-only same-origin API-base injection, inert loopback dependencies, no Playwright route interception, and explicit console/page/HTTP/request-failure evidence. |
| An expired model selection is displayed by extending its lease | Never extend or ignore the original lease. A provider-free UI revalidation may materialize a fresh context only when the unchanged synthetic frame still proves the exact same unique selected appointment, practitioner and waiting area; selection change fails closed. |
| UI hides authority or interrupts reception work | Visible read-only provenance and no-write copy; quiet `aria-live`; no automatic speech/sound; keyboard/touch controls; close/refresh/fallback; focus restoration. |
| Feature accidentally opens broadly | Development-only check, default false, exact synthetic-practice allowlist and explicit occupied-selector flag. |
| Provider failure silently falls back | No provider or deterministic planner fallback for the model-required path; typed unavailable/rejected state; zero release. |
| Retry exceeds call or cost ceiling | Single-use ledgers, two-call/USD 0.50 parent ceiling and immediate stop after first admission. |
| Evidence retains prompt, model text or credentials | Allowlisted hashes/shape/usage only; raw prompt/response/thought/header/token/credential retention forbidden. |
| Test records or runtime residue persist | Exact owned-fixture cleanup, unchanged database truth readback, process/container/network/image absence and no broad prune. |

## Residual claim limits

A4 evidence cannot establish real-patient safety, clinical authority, production
readiness, Australian physical/sovereign processing, a command, a write, a
waiting-time service guarantee or patient-facing suitability.

## Accepted verification result

The live-local provider-free read passes with unchanged database truth and exact
owned cleanup. The occupied selector consumed exactly two calls/USD 0.50: the
first grounded-selector candidate released nothing; one materially distinct
same-fact/singleton correction passed a fresh source veto and deterministic
proofreading. The final loopback HTTPS UI evidence has empty console, page,
HTTP and request-failure arrays and complete server/TLS cleanup. The independent
whole-candidate review passed 113 tests and all bound artifact/source hashes with
no findings before Sol acceptance.
