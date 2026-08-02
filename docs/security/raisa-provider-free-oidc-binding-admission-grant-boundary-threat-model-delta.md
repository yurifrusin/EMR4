# Threat-model delta: provider-free OIDC binding and admission-grant boundary

Date: 2026-08-02

Parent: `docs/security/raisa-provider-free-oidc-start-callback-transport-boundary-threat-model-delta.md`

## New trust boundaries

1. Verified authored-synthetic Microsoft identifiers cross from the verifier
   port into an HMAC-only database resolver.
2. A security-definer function crosses an execution-only capability into exact
   binding read and required audit authority.
3. A raw 256-bit bearer crosses once from server memory to the exact-origin
   callback bridge.

No product, application-session or live-provider boundary opens.

## Threats and controls

| Threat | Control | Failure |
|---|---|---|
| Raw external identity persists | Keyed HMAC every issuer/tenant/object/subject/audience/correlation value before SQL | Residue acceptance fails; transaction denied |
| Subject substitution under same object | Resolver compares issuer, tenant, object and subject HMACs exactly | Rejected audit; no grant |
| Resolver argument bypasses RLS | Exact regex/policy validation, transaction-local HMAC settings and forced-RLS row equality | Function returns no row or aborts |
| Security-definer search-path hijack | `SET search_path = ''`, fully qualified objects, no dynamic SQL, PUBLIC execute revoked | Migration/static check fails |
| Caller gains binding-table authority | Separate execution-only capability; resolver owner is NOLOGIN and not granted to login | Direct-access acceptance fails |
| Grant issuer reads bindings | Separate capability has grant/audit insert only | Privilege acceptance fails |
| Missing audit still releases grant | Resolver audit is mandatory; an after-insert security-definer trigger creates the issued audit and the issuer has no direct audit privilege | Rollback; generic unavailable |
| Partial effects survive role/RLS failure | One explicit transaction and release only after known commit | No bearer returned |
| Bearer recovered from database | Store only separately keyed versioned HMAC; 256-bit CSPRNG bearer | Residue/database assertion fails |
| Bearer replay window is excessive | Exact 60-second database constraint; no renewal or extension | Insert denied |
| Grant crosses surface/origin | Persist exact surface, origin and return target; exact-origin bridge only | No success bridge |
| Raw bearer leaks through URL/cookie/log | Message-body-only release; no URL/header/storage/cookie field; sanitized evidence | Residue and header assertions fail |
| Unbounded active grants exhaust store | Transactional fixed capacity and expiry-aware count | Generic unavailable, no insert |
| Callback silently falls back after issue failure | Injected admission port is mandatory for that transport instance; failures do not render old success | Generic unavailable |
| Issued grant is mistaken for authorization | Grant record and bridge explicitly carry no session/product flags; no redemption import | Static/runtime assertion fails |

## Residual gates

This does not establish redemption, current internal principal truth, an
application session, authentication cookies, product authorization, live
Microsoft interoperability, distributed rate control, production secret
management, incident monitoring, deployment, production or release.
