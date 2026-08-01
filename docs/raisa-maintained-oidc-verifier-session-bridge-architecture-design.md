# Raisa maintained OIDC verifier and session-bridge design

Date: 2026-08-02

Status: `architecture_only_no_runtime_wiring`

## 1. Security invariant

Microsoft Entra may prove one external authentication event. Only the EMR4
backend may bind it to one current internal principal, select practice scope,
load role/practitioner truth, create/revoke a session, and authorise a later
product request. Authentication is not authorization.

```text
surface partition
  -> pre-auth CSRF + exact start command
  -> server-side attempt (state + nonce + S256 PKCE)
  -> tenant-specific Microsoft Entra via maintained MSAL Python
  -> exact callback and one-use attempt consumption
  -> verified tid+oid/sub postconditions
  -> HMAC-only SECURITY DEFINER resolver + required audit
  -> 60-second origin/surface-bound admission grant
  -> exact-origin dialog/opener message (not URL/storage)
  -> CSRF-protected redemption in the original cookie partition
  -> second binding resolution + fresh internal truth reload
  -> atomic grant consume + parent/surface session + audit commit
  -> Set-Cookie after commit
  -> endpoint-owned authorization on every later product request
```

No arrow exists from email, domain, Office signed-in state, Microsoft groups,
directory roles or token scopes to EMR4 user, practice, role or capability.

## 2. Maintained verifier adapter

The future `MicrosoftOidcProtocolAdapter` is the sole provider-facing port. It
wraps a pinned, reviewed MSAL Python confidential client constructed from one
tenant-specific authority and one exact client audience. It exposes only:

```text
begin(attempt_policy) -> authorization_uri + opaque_attempt_reference
complete(encrypted_flow_record, exact_callback_parameters)
  -> VerifiedMicrosoftAuthentication | ProviderProtocolFailure
```

`VerifiedMicrosoftAuthentication` contains bounded verified facts: policy
version, issuer, audience, tenant ID, object ID, subject, authentication time,
issued/not-before/expires times and a library verification receipt. It contains
no raw ID/access/refresh token and no Microsoft role or product authority.

The adapter accepts callback parameters only from the exact configured route;
it passes the previously stored MSAL flow record and response once to
`acquire_token_by_auth_code_flow()`. It accepts `id_token_claims` only from a
successful library result, then enforces exact EMR4 postconditions. It never
calls `jwt.decode`, never selects `alg`/`kid`/`jwks_uri` from untrusted input,
never disables issuer/audience/signature/time validation and never tries a
second provider/tenant/verifier.

One bounded network timeout, tenant-specific metadata and library-managed key
rollover are future implementation requirements. Unknown/stale keys, metadata
failure, provider ambiguity or any library error deny generically. A future
fault-injection gate must exercise multiple keys, rollover and outage before
live authority is considered.

## 3. Authorization-attempt state

One future short-lived server-side record contains:

- `attempt_reference_hash`, `state_hash`, `nonce_hash`;
- envelope-encrypted MSAL flow record including the PKCE verifier;
- exact provider/policy/client/tenant references;
- exact `surface`, `origin`, `return_target` enum and correlation reference;
- `created_at`, `expires_at`, `consumed_at` and optimistic version; and
- no email, Office account, raw tenant/object value, token or product data.

The raw state appears only in the authorization request/callback. The raw nonce
and verifier remain server-side. At callback the record is locked, exact
state/surface/origin/expiry are checked, and `consumed_at` is set in the same
transaction that admits the one provider exchange. A callback replay, timeout
or provider failure requires a new start.

Only server enums choose post-login destinations. `return_url`, `next`, a
client origin, forwarded host or provider error text can never become a
redirect target. Proxy-derived scheme/host is accepted only through the
already reviewed one-hop proxy trust policy.

## 4. Database bootstrap capability

### 4.1 Roles

| Role | Login | Inherits | Table DML | Function execution | Purpose |
|---|---:|---:|---|---|---|
| deployment login | yes | no | none | through explicit `SET LOCAL ROLE` | finite pooled connection only |
| identity-bootstrap capability | no | no | none | exact resolver only | provider-key to principal candidate |
| resolver routine owner | no | no | binding `SELECT`, audit `INSERT` only | owns exact function | constrained `SECURITY DEFINER` body |
| application-auth capability | no | no | accepted session/audit grants under RLS | existing session operations | session creation after practice is known |
| migration/table owner | no runtime login | no | ownership | none to app | DDL only |

Every role is `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
NOBYPASSRLS`. No runtime role is a member of an owner role.

### 4.2 Exact resolver

The future function has one versioned signature, for example:

```text
resolve_application_identity_v1(
  provider,
  issuer_reference_hmac,
  tenant_reference_hmac,
  object_reference_hmac,
  subject_reference_hmac,
  correlation_reference_hmac,
  policy_version,
  occurred_at
) -> binding_ref, user_ref, practice_ref, binding_version
```

It is `SECURITY DEFINER SET search_path = pg_catalog`; all application tables,
types and functions are schema-qualified. `PUBLIC` and every unrelated role
have no execute privilege. The bootstrap capability has execute only and no
schema/table/sequence privilege beyond what function invocation requires.

The routine validates fixed provider/policy/algorithm prefixes and HMAC lengths,
sets transaction-local lookup/correlation settings, performs one exact active
binding lookup under forced RLS and inserts one typed audit event. RLS policies
for the routine owner require row HMACs to equal those transaction-local
settings. A found row determines practice scope. A not-found result inserts one
practice-null denial event. More than one row is an invariant error and denies.
Only after audit insert succeeds may the function return the four bounded
references. Exceptions are remapped to fixed reason codes outside the function;
SQL text, connection data and raw identifiers never reach a client or log.

This function is the only pre-practice data path. It cannot create, update,
revoke or recover a binding; cannot select arbitrary rows; cannot load role,
patient, appointment, diary or clinical data; and cannot create a session.

## 5. Admission grant

After maintained-library verification, the callback computes versioned HMAC
references in the application boundary and calls the resolver. A successful
resolution creates one admission-grant row with:

- a SHA-256/HMAC digest of a 256-bit CSPRNG bearer;
- binding/user/practice references and exact binding version;
- external-key HMAC reference and provider-policy version;
- exact source surface, origin, audience and return-target enum;
- correlation, issued, expiry (at most 60 seconds), status and version; and
- no raw identity, provider credential, token, claim or product data.

The raw grant is present only in the callback response body and exact-origin
message to the original opener/dialog parent. It is never a query/fragment,
cookie, log field, document setting, `localStorage`, `sessionStorage` or
IndexedDB value. The bridge page uses `default-src 'none'`, one nonce/hash-bound
inline bridge script, exact `frame-ancestors`, `Referrer-Policy: no-referrer`,
`Cache-Control: no-store`, `X-Content-Type-Options: nosniff` and no third-party
resource.

## 6. Redemption transaction

The original surface calls the future redemption command with the raw grant,
its frozen surface enum and the existing pre-auth CSRF cookie/header. The
backend obtains origin from the reviewed request boundary, never from the body.

One serializable/locking transaction then:

1. hashes and locks the exact active, unexpired grant;
2. compares surface, exact origin, audience, policy and grant version;
3. calls the HMAC-only resolver again and requires the same binding/version;
4. freshly loads current internal user, practice, role and practitioner link;
5. applies active/membership/role/surface policy without Microsoft claims;
6. advances/revokes prior principal generation when required;
7. generates new opaque parent and surface values with a CSPRNG;
8. stores only their hashes and the authoritative internal principal snapshot;
9. marks the grant consumed and writes federation/session/surface audit; and
10. commits once.

Only after commit does the response set the surface cookie and rotate the CSRF
pair. An exception, audit failure, serialization conflict or connection loss
releases no cookie or principal. Concurrent redemptions lock the same row; at
most one commits. A retry after an uncommitted transient failure may re-enter
within the grant TTL; a committed grant can never mint or replay another
session.

No callback or redemption handler reads product/clinical tables. A subsequent
request presents only the surface bearer, and the existing application-auth
runtime checks session hash, generation, surface, origin, audience, idle and
absolute expiry before endpoint-specific authorization.

## 7. Failure and privacy contract

Externally, protocol, tenant, subject, binding, internal-principal, grant and
session failures collapse to `authentication_failed`; required infrastructure
or audit failure collapses to `authentication_temporarily_unavailable`.
Detailed reason codes are metadata-only internal audit.

Logs and traces may retain correlation, policy/library version, decision,
bounded reason, latency, surface and HMAC references. They may not retain raw
state, nonce, PKCE, code, token, tenant/object/subject, email/name, admission
grant, session bearer, CSRF token, document, patient or clinical content.
Provider error descriptions are normalized before logging.

Rate admission is required at start, callback and redemption for origin/IP
bucket plus state/grant digest, with the first blocked request audited. This
architecture does not claim distributed enforcement, paging or SIEM.

## 8. API and UI behavior

The start and redemption surfaces are REST commands/protocol operations. The
callback is a provider protocol endpoint. None is GraphQL. A later GraphQL
binding-status field may return provider, active/revoked state and last-used
time only after administrator authorization; it cannot perform account linking
or expose external identifiers.

Word desktop, Word Online and native Diary use one backend protocol. Office
signed-in state may affect which account Microsoft itself presents, but the
taskpane sends no email/domain/role/practice hint and silently acquires no
identity. The admission-grant message reconciles cookie partitions without
making the dialog a parallel session authority.

## 9. Closed implementation decisions

Still closed are the actual dependency/version addition, secret versus
certificate credential, app registration/redirect host, production key/HMAC
custody, attempt/grant schema and retention migration, database roles/functions,
FastAPI handlers, callback bridge code, real identity bindings, recovery UX,
organisational Office deployment, distributed rate limiter, alerting/SIEM,
product-read connection, production, release and protected integration.
