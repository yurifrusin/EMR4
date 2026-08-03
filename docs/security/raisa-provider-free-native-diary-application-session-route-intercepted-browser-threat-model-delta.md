# Threat-model delta: native-Diary route-intercepted application-session browser rehearsal

Date: 2026-08-03

Parent: `provider_free_native_diary_application_session_ui_composition_pass`

## Boundary change

No product boundary changes. A disposable real Chromium process now exercises
the accepted default-off static composition with closed authored-synthetic
route fixtures. This adds browser execution and DOM/network evidence only.

| Threat | Control | Failure outcome |
|---|---|---|
| Route-intercepted evidence is mislabelled live | Exact `evidence_mode=route_intercepted_browser`; claims-not-made include live backend/PostgreSQL and real injection | Candidate rejected |
| A request reaches a real backend or external provider | All requests pass one handler; exact local assets continue, exact API paths are fulfilled, every other non-loopback host is aborted and recorded | Candidate rejected on any blocked host; request never leaves Chromium |
| API fixture broadens into arbitrary product access | Closed path-and-method dispatcher; unknown `/api/v1/` paths return 404, wrong methods on known paths return 405, and both are recorded | Candidate rejected |
| Synthetic token is mistaken for real identity | JWT-shaped value is unsigned, authored locally, carries only `Receptionist` and expiry, never leaves the context and grants no claimed authority | Evidence remains synthetic and non-authoritative |
| Enabled success silently uses legacy practitioner transport | Capture phase-specific counters immediately after enabled render and before transition | Any GraphQL or REST practitioner count rejects candidate |
| Disable transition allows a held row to render | Hold one real fixed-reader promise, disable the bootstrap, use visible Refresh, then release the stale envelope | Stale name count must remain zero |
| Transition evidence hides the expected legacy read | Capture post-disable counters before releasing the stale result | Exactly one GraphQL and zero REST practitioner requests required |
| Enabled failure falls back or partially renders | Fixed generic marker, zero GraphQL/REST practitioner calls, hidden grid container and zero grid children | Candidate rejected on fallback or DOM residue |
| Feature-off path accidentally loads the new module | Bootstrap property absent; module-request ledger must be empty | Candidate rejected |
| Feature-off legacy behavior is only inferred from network | Open the visible booking modal and read the exact practitioner option | Candidate rejected unless legacy name renders |
| Browser console hides framework/runtime failure | Record every Chromium console error; known missing hosting-policy path is fulfilled from the exact committed default-off policy file | Candidate rejected on any console error |
| Static fixture changes without evidence | Hash the exact committed Diary HTML/JS/modules and hosting-policy source | Reproduction mismatch rejects candidate |
| Direct page internals fabricate render evidence | Page-state changes are limited to pre-script fixture setup and held-reader transition; rendering and refresh use ordinary page scripts and visible controls | Candidate rejected by static/test review |
| Screenshot collection expands cost or captures unintended UI | Root review removed screenshots; evidence uses bounded DOM/state and network/module ledgers | No image artifact is created |
| `app.main`, database or provider runtime starts | Script imports only standard-library static-server support and Playwright; static scans forbid application/database/runtime imports | Candidate rejected |
| User-owned branding is captured | No branding path is opened or referenced by the harness; exact-path integration remains Sol-owned | Candidate rejected |

## Residual risk and gates preserved

The rehearsal does not prove a live local or deployed backend, PostgreSQL,
cookie/session transport, real authorization or audit, real identity/data,
cross-tab transition delivery, Firefox/WebKit behavior, accessibility,
usability, XSS/supply-chain controls, default-on operation, deployment,
production or release suitability. Providers/models, memory/RAG, patient or
clinical data, product commands/writes, protected evidence/refs and
`docs/branding/` remain closed.
