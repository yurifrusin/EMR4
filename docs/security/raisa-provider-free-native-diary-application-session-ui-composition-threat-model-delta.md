# Threat-model delta: native-Diary default-off application-session UI composition

Date: 2026-08-03

Parent: `provider_free_native_diary_application_session_practitioner_reconciliation_pass`

## Boundary change

The native Diary gains a static, default-off branch around one trusted injected
fixed practitioner-directory read. No backend route, authentication rule,
product scope or write boundary changes. Client generation remains suppression
metadata and never becomes authentication, authorization, audit or command
authority.

| Threat | Control | Failure outcome |
|---|---|---|
| Accidental default-on or truthy-string enablement | Only `bootstrap.enabled === true`; missing, false, malformed and non-boolean states stay legacy | Existing bearer GraphQL/REST path runs unchanged |
| Enabled bootstrap silently falls back after failure | Enabled branch is selected before legacy logic and propagates only generic rejection | No bearer or REST request follows the attempt |
| Caller injects scope, identity, authority or arbitrary query data | Recursively closed exact three-key bootstrap; no arguments passed to fixed reader | Bootstrap rejected before reader invocation |
| Trusted reader changes inside one lifecycle | First reader identity is fixed for the long-lived composition | Changed reader fails closed before invocation |
| Late response overwrites newer directory | Canonical accepted reconciler and latest request revision | Superseded ticket rejected before render |
| Response survives invalidation or generation change | Explicit invalidation and strict monotonic generation advance | Outstanding ticket rejected before render |
| Forged/replayed ticket or malformed/authority-bearing response crosses egress | Weak identity, consume-before-callback and exact response admission | Fixed rejection; no row callback |
| Reader exception leaks error or leaves replayable ticket | Error is not retained; ticket is consumed with inadmissible input and a fixed reason is returned | `fixed_read_failed`; no row or raw error released |
| Snapshot leaks reader, row, identity, secret or authority data | Snapshot copies only bounded reconciler counters and lifecycle metadata | Static/dynamic privacy test fails |
| New module performs direct HTTP/storage/auth/provider/write work | Static forbidden-surface scan of both published modules | Candidate rejected |
| Published reconciler drifts from accepted source | CRLF-to-LF canonical byte parity | Candidate rejected |
| GraphQL becomes a command or broader read tunnel | API Spine static checks and closed contract | Candidate rejected |
| User-owned branding is captured | Exact-path staging and cached-path guard | Commit forbidden |

## Residual risk and gates preserved

The static harness does not prove browser execution, real injection timing,
HTTP/backend/PostgreSQL behavior, DOM rendering, cross-tab invalidation, XSS or
supply-chain controls, usability, deployment or production suitability.
Providers/models, memory/RAG, real identity, patient/clinical/document data,
new API scope, commands/writes, `app.main`, cloud/IAM, deployment, production,
release, protected evidence/refs and `docs/branding/` remain closed.
