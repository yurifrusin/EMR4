# Threat-model delta: maintained OIDC verifier and session bridge

Date: 2026-08-02

Status: `architecture_only_provider_free`

Parent: `docs/security/raisa-real-identity-microsoft-federation-boundary-threat-model-delta.md`

## 1. Scope and claim

This delta models the newly authorised architecture between one external
Microsoft Entra authentication attempt and one EMR4 application-session cookie.
It covers maintained-library verification, pre-practice PostgreSQL bootstrap,
partition-safe admission-grant handoff and session creation. It contains no
live provider, real identity, package change, route, database object, product
read, deployment or production result.

## 2. Protected assets

- authorization state, nonce, S256 PKCE verifier and provider code;
- Microsoft ID/access token material and verified immutable `tid`/`oid`/`sub`;
- the HMAC identity reference key and version;
- external-identity binding, internal user/practice/role/practitioner truth;
- short-lived admission grants, parent/surface session bearers and CSRF values;
- PostgreSQL role/function/RLS boundaries and append-only security audit; and
- the invariant that no product read occurs before backend session and endpoint
  authorization.

## 3. Trust boundaries

| Boundary | Accepted input | Never grants |
|---|---|---|
| Browser or Office surface -> start | exact surface enum, server-known origin, CSRF, return enum | email, account, tenant, user, practice or role |
| Backend -> Microsoft Entra | tenant-specific MSAL flow with exact redirect, state, nonce, S256 PKCE | arbitrary authority, discovery URL or scope |
| Entra callback -> verifier | exact callback parameters correlated to one stored attempt | client-decoded claims or a supplied token |
| Verifier -> federation admission | library-verified bounded facts | Microsoft group/role/scope as EMR4 authority |
| App -> PostgreSQL bootstrap | fixed HMAC references through exact function | table-owner access, raw identifier or arbitrary query |
| Callback dialog -> original surface | 60-second one-use origin/surface-bound admission grant | session cookie, parent bearer or product capability |
| Redemption -> application auth | locked grant, repeat binding resolution, fresh internal truth | cached role/practice or client-selected scope |
| Session -> product endpoint | opaque surface bearer plus CSRF where required | generic access; each endpoint still authorizes |

## 4. Threats, controls and residual gates

| Threat | Attack path | Frozen control | Residual gate |
|---|---|---|---|
| Login CSRF / session swapping | attacker starts a flow and forces victim callback | one stored user-agent-bound state, nonce and S256 PKCE; exact callback correlation; pre-auth CSRF on start/redeem | real-browser fault injection |
| Code interception or injection | stolen/injected code redeemed by another client | confidential backend, exact redirect, S256 verifier never sent to browser, attempt consumed before one redemption | live MSAL/Entra interoperability |
| Callback replay | repeat code/state or parallel callback | row lock, single-use attempt, provider exchange at most once, new start after failure | durable attempt schema |
| Authorization-server mix-up | callback from common/foreign/malicious issuer | tenant-specific authority and metadata only; exact issuer, audience, `tid`; no arbitrary discovery | configured tenant/app registration review |
| Algorithm/JWKS confusion | `none`, symmetric key, attacker `kid`/`jku`/`jwks_uri` | MSAL owns verification; no untrusted algorithm/key URL; no fallback parser | dependency and rollover fault tests |
| Emergency key rollover outage | new legitimate key is initially unknown | maintained library tenant metadata/key rollover with bounded network timeout; uncertainty denies | operational cache/timeout/SLO proof |
| Library supply-chain defect | compromised/outdated OIDC package | MSAL Python chosen; future exact pin, hash, SBOM, licence, vulnerability and update policy gate | dependency addition needs fresh authority |
| Token/code leakage | debug logs, traces, exception text, browser storage or URL | no raw provider material in logs/storage/URL; normalized errors; no-store callback; provider result discarded after HMAC facts | telemetry redaction tests |
| Mutable-claim account takeover | email/domain/name/Office identity matches another user | only exact immutable tenant-local `tid`+`oid` prebinding; `sub` verified; no JIT or email linking | real binding commands remain closed |
| Microsoft-role privilege escalation | groups/roles/scopes copied into EMR4 | fresh internal role/practitioner reload; claims never mapped | endpoint authorization proof |
| Table-owner shortcut | runtime resolves unknown identity as migration/table owner | LOGIN has no table grants; execute-only NOLOGIN bootstrap; constrained `SECURITY DEFINER` owner | migration and privilege tests |
| Security-definer injection | attacker controls search path, SQL identifiers or arbitrary input | `search_path=pg_catalog`, schema-qualified objects, fixed signature/types, no dynamic SQL, PUBLIC execute revoked | database implementation review |
| Bootstrap over-read | resolver can enumerate all bindings/practices | forced RLS tied to exact transaction-local HMACs; four-field bounded return; generic denial | explain/privilege/RLS probes |
| Unknown-binding audit bypass | no practice is known so runtime uses owner connection | exact resolver inserts practice-null typed denial under narrow audit policy | retention/SIEM policy |
| RLS context confusion | stale setting or pooled connection exposes prior practice | transaction-local settings only; finite transaction; RESET/discard-on-return; repeat exact practice binding | pooled-connection adversarial proof |
| Admission-grant theft | dialog message intercepted or grant placed in URL/storage | 256-bit bearer, digest-only persistence, exact target origin, body message only, 60-second expiry, surface/origin/audience bind | Office/native browser acceptance |
| Cross-partition session confusion | dialog cookie is mistaken for taskpane/native cookie | callback sets no session cookie; original partition redeems and receives its own surface cookie | real Word desktop/Online proof |
| Grant replay/race | two surfaces redeem one grant | row lock and atomic single transition; same binding/version; at most one commit | PostgreSQL concurrency proof |
| Binding/principal TOCTOU | account revoked after callback but before session | re-resolve binding and freshly reload user/practice/role/practitioner at redemption | real internal-store bridge proof |
| Session fixation | attacker supplies or preserves a prior session | always mint new parent/surface CSPRNG values; raw parent never client; rotate CSRF and generation | live cookie/session proof |
| Session/audit split brain | cookie released when audit/session transaction fails | grant consume, sessions and audits commit together; `Set-Cookie` only after commit | database fault-injection proof |
| CSRF after login | browser automatically attaches partitioned cookie | existing `__Host-` CSRF cookie/header, exact origin, no state-changing GET; SameSite is defense in depth | rendered-host matrix |
| Open redirect / exfiltration | attacker controls `next`, Host or forwarded headers | server-side return enums, exact origin map, reviewed one-hop proxy trust, no credential in redirect URL | deployment-host allowlist |
| Enumeration | error distinguishes tenant, binding, user or role | two generic external failures; bounded internal reason only | UX and response-timing review |
| Brute force / denial of service | flood start/callback/grant/HMAC resolver | bounded start/callback/redeem rate keys and audit first block; timeouts; no retry fanout | distributed limiter/paging closed |
| Product read before authorization | callback loads diary/patient/clinical data | callback/redeem imports identity/session ports only; endpoint-owned session and authorization on later request | live route import/query audit |

## 5. Abuse cases that must remain deterministic

1. A valid personal or foreign-tenant Microsoft account receives the same
   generic failure as an unknown local binding.
2. A valid token paired with a wrong state, nonce, PKCE verifier, issuer,
   audience, tenant or consumed attempt releases no grant.
3. A Microsoft email or Office signed-in account matching an internal user
   cannot create or select a binding.
4. An unknown binding is audited without an owner connection and returns no
   practice/user reference.
5. A stolen grant used from a different surface or origin fails and cannot
   consume the legitimate redemption.
6. Binding revocation, role/practice change or practitioner unlink between
   callback and redemption prevents the session.
7. Two concurrent grant redeemers produce at most one session and cookie.
8. An audit, transaction or commit failure releases neither session nor cookie.
9. A valid session still cannot read product data through an endpoint whose
   fresh role/practice/resource authorization denies.

## 6. Privacy and audit boundary

Permitted audit fields are correlation/HMAC references, policy/library version,
surface, typed event, decision, bounded reason, binding/user/practice references
when known, timing and session-reference hashes. Forbidden fields are raw
state, nonce, PKCE, code, token, tenant/object/subject, email/name, provider
description, grant, session/CSRF bearer, return URL, document, patient,
appointment, diary or clinical content.

The resolver must audit a zero-match denial before returning. Successful grant
redemption requires one transaction containing binding resolution, grant
consumption, session/surface creation and required audit. If retained
infrastructure-error audit cannot be recorded, the response remains a generic
service error and no authority is released.

## 7. Explicitly closed gates

- package/dependency or licence acceptance;
- Entra app registration, tenant configuration, credential/certificate and
  redirect host;
- live discovery, JWKS, token exchange, Microsoft/Graph/Office identity call;
- real identity binding or account-link/recovery command;
- attempt/grant tables, roles, functions, RLS or migrations;
- FastAPI callback/start/redemption or bridge-page implementation;
- live app session, internal/product read, Office organisational deployment;
- distributed abuse control, paging/SIEM and retention policy;
- production key custody, deployment, protected integration and release.

## 8. Residual assessment

The architecture reduces the dominant account-takeover, confused-deputy,
cross-partition and owner-privilege risks without claiming implementation.
Residual risk remains high until the selected library, database capability,
real browser/Office handoff, atomic session path, operational controls and
endpoint authorization are independently implemented and exercised under
fresh authority.
