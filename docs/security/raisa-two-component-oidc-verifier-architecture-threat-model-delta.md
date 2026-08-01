# Threat-model delta: two-component OIDC verifier architecture

Date: 2026-08-02
Parent: maintained OIDC verifier/session-bridge architecture

## New trust boundary

The corrected design introduces an explicit seam between a protocol client and a cryptographic verifier. MSAL handles a Microsoft authorization-code exchange over TLS. Authlib/JOSE RFC independently establishes which ID-token claims are admissible. The future adapter is responsible for passing only a transient raw ID token across that seam and for treating all MSAL-decoded claims as untrusted.

## Threats and controls

| Threat | Control | Failure result |
|---|---|---|
| TLS-valid but forged or substituted ID token | Authlib verifies RS256 signature against the tenant discovery JWKS | Generic deny |
| Algorithm confusion or symmetric-key substitution | Exact RS256 allow-list; discovery must advertise RS256 | Generic deny |
| Tenant or issuer confusion | Server-owned tenant-specific v2 discovery, exact issuer and exact `tid` postcondition | Generic deny |
| Stale key set during rollover | Authlib cache plus one forced refresh on unknown `kid` | Admit only after valid refreshed signature; otherwise deny |
| Attacker-selected discovery/JWKS | Fixed Microsoft host and tenant path; ignore token `jku`; no request-selected metadata | Generic deny |
| Replay or callback substitution | Stored MSAL flow, exact state, nonce, S256 PKCE, atomic one-use attempt | Consume or deny; never retry provider exchange |
| Authorization code disclosure through URLs | `response_mode=form_post`, POST form callback, no-store/no-referrer response | No code in query/history/referrer |
| Oversized token or diagnostic leakage | 16 KiB pre-parse bound; normalized exceptions; no raw token logging/persistence | Generic deny |
| Privilege from mutable identity hints | Email, domain, names, groups, roles and scopes are non-authoritative | No binding, role or session |
| Refresh/access token expansion | Exclude `offline_access`; discard access token; no Graph or product scope | No token retention or downstream call |
| Verifier fallback under outage | No custom or alternate verifier | Authentication temporarily unavailable |
| Metadata staleness | Verifier client lifetime at most 24 hours plus unknown-key refresh | Recreate client or deny |

## Dependency risks

We pin the two top-level components and the direct cryptographic implementation. Authlib 1.7.2 is above the fix for CVE-2026-41479, and JOSE RFC 1.7.4 is above the fix for CVE-2025-65015. Package admission does not make the future adapter safe by itself; subsequent work must preserve the exact port, error, token-lifetime and metadata-coherence controls and must rerun dependency audit at implementation time.

## Residual risk

The offline harness cannot prove Microsoft availability, tenant configuration, Office cookie behavior, distributed abuse resistance, or production secret handling. It also does not create an EMR4 identity binding. Those remain closed until separately authorised live-local and provider tranches.
