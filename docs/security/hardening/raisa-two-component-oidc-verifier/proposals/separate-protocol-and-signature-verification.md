# Separate protocol and signature verification

## Opportunity

We need an identity-admission property that the current protocol client does not supply. The token endpoint exchange may be TLS-protected, but the parent contract specifically requires a trusted signing key, issuer, audience, nonce and lifetime checks before an external principal exists.

## Current state and evidence

MSAL 1.37.0 appropriately creates and redeems a confidential-client authorization-code flow, including state, nonce and S256 PKCE. Its ID-token helper decodes without performing an independent JWS signature verification (E004, E005). Microsoft documents signature/key validation and key rollover as token-validation responsibilities (E008, E009).

## Option: TLS-only MSAL

We could revise the stated property downward and rely on the successful token-endpoint TLS exchange. Security would remain below the frozen admission requirement. Performance and memory are minimal, reliability has fewer local dependencies, and migration is zero, but operability would encode a false verifier boundary. We reject it.

## Option: MSAL plus Authlib verifier

We retain MSAL's protocol role and pass only the transient raw ID token to Authlib 1.7.2 with JOSE RFC 1.7.4. Security gains independent RS256/JWK and OIDC claim validation. Performance adds one local cryptographic verify, memory adds one bounded metadata/key cache, and reliability gains one maintained unknown-key refresh before fail-closed denial. Operability requires observing two explicit components; migration is limited to a narrow future adapter. We select it.

## Option: one full OIDC client

We could replace MSAL and allow Authlib or another full OIDC client to own the entire flow. Security can be coherent, performance and memory are similar, and steady-state operation could be simpler. Migration would invalidate the existing MSAL flow evidence and reopen callback, scope and provider-compatibility decisions. We defer it.

## Option: custom PyJWT/JWKS glue

We could build discovery, cache, refresh and claim admission around the existing PyJWT dependency. It may be lean in CPU and memory, but security and reliability depend on custom concurrency, rollover, algorithm and outage logic. Operability inherits a permanent bespoke verifier. We reject it.

## Selected hardening

We select the two-component seam, exact pins, `form_post`, a 16 KiB token bound, RS256 only, a 60-second leeway, one unknown-key refresh, a 24-hour verifier-client maximum lifetime, normalized errors and no fallback. The next adapter tranche must implement this frozen contract and no broader authority.
