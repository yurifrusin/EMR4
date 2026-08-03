# Threat-model delta: native-Diary practitioner reconciliation

Date: 2026-08-03

Parent: `provider_free_native_diary_application_session_practitioner_runtime_pass`

## Assets and trust boundary

The only asset crossing this task-local boundary is the accepted display-safe
authored-synthetic practitioner projection. Trusted composition code owns the
client lifecycle generation and supplies already-returned fixed-read results.
The reconciler is not an authentication or authorization component and cannot
upgrade client metadata into server authority.

## Threats and controls

| Threat | Control |
|---|---|
| Late response overwrites a newer directory | Strict latest request revision; the older ticket returns `request_superseded` before render. |
| Response survives logout/revocation signal | `invalidateSession()` deactivates the lifecycle; no known outstanding ticket renders. |
| Response from an earlier lifecycle renders after renewal | Strictly increasing generation and exact generation check. |
| Ticket forged or moved between reconciler instances | WeakMap object-identity provenance; visible ticket fields are insufficient. |
| Successful ticket replay | Consume before callback; callback failure cannot restore it. |
| Malformed or authority-bearing response crosses egress | Exact-key envelope and row admission; unknown fields and unsuccessful status fail closed. |
| Client retains directory data | No response row is stored; weak ticket identity avoids an unbounded strong-reference ticket history. |
| Diagnostics leak identity/session material | Snapshot and evidence are restricted to bounded counts, generation/revision metadata, fixed labels and hashes. |
| Client generation is mistaken for backend proof | Documentation and evidence explicitly classify it as trusted client lifecycle suppression only. |

## Residual risks

- The current server response does not carry a cryptographically or
  server-bound generation. A mounted client must establish its lifecycle
  generation in trusted composition code and continue relying on the backend
  for authentication, authorization, revocation and audit.
- This browserless proof does not exercise fetch cancellation, DOM rendering,
  browser history, tabs, service workers or mounted product code.
- JavaScript executes in the future host's client trust domain; XSS and supply
  chain controls remain product-integration concerns.

## Gates preserved

No provider/model, database, network, browser, Office, Bernie/Davida work cell,
proofreader, command, event, write, patient/clinical data, real identity,
deployment, production, release, protected evidence/ref or branding authority
is added.
