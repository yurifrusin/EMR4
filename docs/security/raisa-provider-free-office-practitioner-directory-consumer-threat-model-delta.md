# Threat-model delta: provider-free Office practitioner-directory consumer

Date: 2026-08-02

Parent: `docs/security/raisa-provider-free-session-practitioner-directory-read-bridge-threat-model-delta.md`

## New trust boundaries

1. One task-delivered application-session/CSRF pair enters an actual Office
   cookie partition.
2. One fixed GraphQL directory response crosses into a narrow taskpane renderer.
3. Two authored-synthetic display names and optional role/location labels become
   visible in the tested Office host.

No document, patient, clinical, provider, real-identity or product-write
boundary opens.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Wrong Office host consumes a session | Manifest-bound server surface plus `Office.onReady` host-class equality before enabling the button | Disabled and sanitized failed result; zero product request |
| Task page reload reissues authority | One delivery per surface; consumed session/CSRF material is not rendered again | Inert unavailable page |
| Client chooses a broader query | Compile-time exact document/variables; accepted server parser independently rejects aliases, fragments, directives, introspection, practice-id-only and mutation shapes | Generic failure; no product SQL |
| Cross-site request replays cookies | Exact origin, surface-bound subapplication, CSRF cookie/header equality and partitioned Secure HttpOnly cookies | 401/403; no rows |
| Unsafe response reaches DOM | Closed key/type/active validation and `textContent`/created text nodes only | Generic failure; no partial render |
| Error detail leaks backend structure | No raw GraphQL/HTTP/SQL text in UI or result schema | Fixed action-oriented copy only |
| Read survives session revocation | Required authorization audit before release, immediate logout and post-logout backend rejection | Result cannot pass |
| Evidence leaks synthetic/product/session identifiers | Counts/booleans only plus raw-value residue scan | Acceptance fails |
| Task harness is mistaken for a product mount | Separate construction, absent from `app.main`, fresh development manifests and complete owned cleanup | Static/cleanup gate fails |

## Residual gates

This does not establish real identity, live Microsoft federation, general
session-backed GraphQL mounting, patient/clinical or document-read safety,
product-table RLS, broader product reads, product writes, distributed abuse
resistance, monitoring/SIEM, organisational deployment, production or release.
