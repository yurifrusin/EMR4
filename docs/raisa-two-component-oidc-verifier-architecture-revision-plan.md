# Raisa two-component OIDC verifier architecture revision plan

Date: 2026-08-02
Status: authorised architecture and dependency-admission tranche

## Outcome sought

We will correct the maintained-verifier architecture before any adapter exists. Microsoft Authentication Library (MSAL) will own the tenant-specific confidential-client authorization-code exchange, while Authlib and JOSE RFC will independently verify the raw ID token before EMR4 may derive an external principal. We will admit exact dependency versions and prove the seam offline with authored-synthetic tokens.

## Authority

This tranche may revise architecture, API-spine and threat-model artifacts; review and pin verifier dependencies; add provider-free acceptance fixtures; and make necessary task-branch commits. It may not mount routes, contact Microsoft, use real identity, create an application session, read product data, change database truth, deploy, release, or move protected refs.

## Acceptance

The tranche passes only when:

1. the ownership boundary states that MSAL claims are never identity-admission evidence;
2. Authlib 1.7.2 with JOSE RFC 1.7.4 verifies signature, issuer, audience, nonce and time claims with RS256 only;
3. unknown `kid` causes one library-owned key-set refresh and failure after that refresh denies admission;
4. tenant, discovery, issuer and JWKS locations are server-owned and coherent;
5. MSAL requests no application or Graph scopes, excludes `offline_access`, uses S256 PKCE and `response_mode=form_post`;
6. raw tokens are bounded to 16 KiB, transient, never logged or returned, and all verifier errors are normalized;
7. exact package versions, licences, hashes, advisories and alternatives are recorded;
8. provider-free tests demonstrate the seam without mounting an application adapter; and
9. all evidence says zero provider calls, real identities, sessions, product reads, database writes and deployments.

## Work sequence

We will first freeze the component ownership and metadata-coherence contract. We will then record the candidate comparison and systemic hardening portfolio, revise the non-mounted OpenAPI contract, add exact dependency pins, and run an offline signed-token harness. After focused and regression checks, we will close out only the architecture/dependency tranche. The runtime adapter remains a separately authorised descendant.

## Protected boundary

The user-owned `docs/branding/` directory is concurrent work and excluded from staging, testing and evidence. Protected refs remain untouched.
