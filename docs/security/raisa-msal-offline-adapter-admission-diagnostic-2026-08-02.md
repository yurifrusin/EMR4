# MSAL offline adapter-admission diagnostic

Date: 2026-08-02

Result: `revision_required`

## Authorised question

Determine whether a current supported MSAL Python dependency can satisfy the
accepted maintained-verifier architecture before admitting a route-free,
provider-free adapter implementation.

## Dependency review

MSAL Python 1.37.0 is the latest stable release; 1.38.0 is currently a release
candidate. The stable package is MIT licensed, declares Python 3.9 or later,
supports Python 3.14, and requires `requests>=2,<3`, `PyJWT[crypto]>=1,<3` and
`cryptography>=2.5,<51`. Those bounds are compatible with the repository's
current Python 3.14 environment and pinned PyJWT 2.13.0 and cryptography
48.0.1. Its wheel SHA-256 is
`dd17e95a7c71bce75e8108113438ba7c4a086b3bcad4f57a8c09b7af3d753c2d`;
its source archive SHA-256 is
`1b1672a33ee467c1d70b341bb16cafd51bb3c817147a95b93263794b03971bec`.
`pip check` passed and `pip-audit -r requirements.txt` reported no known
vulnerabilities while the candidate pin was temporarily present.

Primary sources:

- https://pypi.org/project/msal/
- https://github.com/AzureAD/microsoft-authentication-library-for-python/releases/tag/1.37.0
- https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/1.37.0/LICENSE
- https://raw.githubusercontent.com/AzureAD/microsoft-authentication-library-for-python/1.37.0/setup.cfg

## Admission blocker

The package is suitable for confidential-client authorization-code protocol
handling, including generated state, nonce and S256 PKCE, but it does not meet
the accepted verifier contract as written. In MSAL 1.37.0,
`oauth2cli.oidc.decode_id_token()` decodes the JWT payload and checks issuer,
audience, nonce and time-related claims. Its source explicitly relies on TLS
validation of the direct token-endpoint response in place of validating the ID
token signature. It does not retrieve a JWKS, validate the JWS signature or
prove signing-key rollover for this code-flow result.

That conflicts with the accepted parent requirements that MSAL itself own:

- ID-token signature validation;
- an allowed signing algorithm;
- trusted signing-key establishment; and
- signing-key rollover.

Microsoft's current OIDC guidance separately says that web applications using
ID tokens to establish a session should use a token-validation library and
validate the signature and claims. The EMR4 adapter would establish the input
to an application session, so silently weakening the parent invariant to
token-endpoint TLS alone is not admitted.

Primary sources:

- https://raw.githubusercontent.com/AzureAD/microsoft-authentication-library-for-python/1.37.0/msal/oauth2cli/oidc.py
- https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc
- https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens

## Additional contract reconciliation

MSAL treats `openid`, `profile` and `offline_access` as reserved scopes. Passing
`openid profile` directly to `initiate_auth_code_flow()` raises `ValueError`.
The future adapter would need to pass an empty resource-scope list and construct
the confidential client with `exclude_scopes=["offline_access"]`; MSAL would
then place exactly `openid profile` on the wire. This is compatible with the
parent no-refresh-token boundary but must be represented explicitly in a
revised contract.

## Safe dispositions

1. Recommended: retain MSAL 1.37.0 for the Microsoft authorization-code
   protocol, but separately review and admit a maintained OIDC/JWS validation
   component that pins issuer, audience and algorithms and owns discovery,
   JWKS caching and rollover. This changes the parent's "MSAL-only verifier"
   decision and requires fresh package/licence/security authority.
2. Not recommended: revise the security invariant to accept MSAL's direct
   token-endpoint TLS validation without JWS verification. This is a material
   weakening and does not match the accepted threat model.
3. Rejected without new architecture: add hand-written PyJWT/JWKS glue. The
   parent deliberately forbids custom JWT/JOSE fallback because it recreates
   algorithm, key-selection, cache and rollover hazards.

## Side effects and residue

No Microsoft/provider call, discovery request, real identity, route, database
object, session, product read, cloud/IAM mutation, deployment, protected-ref
movement or Pages rebuild occurred. The candidate runtime dependency and
adapter source were not retained after the gate failed. The local review
installation was removed. Dependabot alert 17 remains native-open and
unchanged. User-owned `docs/branding/raisa/` remains untouched and excluded.
