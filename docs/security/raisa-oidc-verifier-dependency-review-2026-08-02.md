# OIDC verifier dependency review

Date: 2026-08-02
Disposition: admit exact MSAL + Authlib/JOSE RFC split for a future adapter

## Trigger

Source inspection showed that MSAL Python 1.37.0 decodes an ID token but does not verify its JWS signature. The parent architecture therefore assigned signature/key/rollover ownership to the wrong component. We reviewed maintained packages rather than adding handwritten discovery, cache or rollover code.

## Selected packages

| Package | Version | Role | Licence | Python | Reviewed distribution SHA-256 |
|---|---:|---|---|---|---|
| `msal` | 1.37.0 | Microsoft confidential-client code flow | MIT | `>=3.9` | wheel `dd17e95a7c71bce75e8108113438ba7c4a086b3bcad4f57a8c09b7af3d753c2d`; sdist `1b1672a33ee467c1d70b341bb16cafd51bb3c817147a95b93263794b03971bec` |
| `Authlib` | 1.7.2 | OIDC ID-token verification integration | BSD-3-Clause | `>=3.10` | wheel `3e1faedc9d87e7d56a164eca3ccb6ace0d61b94abe83e92242f8dc8bba9b4a9f`; sdist `2cea25fefcd4e7173bdf1372c0afc265c8034b23a8cd5dcb6a9164b826c64231` |
| `joserfc` | 1.7.4 | Directly pinned JWS/JWK implementation used by Authlib | BSD-3-Clause | `>=3.10` | wheel `32d46c2cd5e3203c13e87a6c61333cab310b1ba80cd54b4c4f386a848a122463`; sdist `b3bc561672ae541b17a9237053b48a03dacddd92d68047b3ecdfb4b5714a88ed` |

Authlib is production/stable, has a long release history and uses PyPI Trusted Publishing. Its current OIDC integration imports the discovery JWKS, verifies with JOSE RFC, validates OIDC claims, caches the key set, and performs one forced refresh when key selection raises `InvalidKeyIdError`. The direct `joserfc` pin makes that reviewed verifier implementation explicit.

The admitted versions are above the published fixes for Authlib CVE-2026-41479 and JOSE RFC CVE-2025-65015. Existing `cryptography==48.0.1` satisfies both packages. `pip check` and a complete requirements audit are acceptance gates, not assumptions.

## Alternatives

| Candidate | Finding | Disposition |
|---|---|---|
| MSAL alone | Protocol behavior is appropriate, but `decode_id_token` relies on the token endpoint TLS exchange and does not verify JWS | Retain for protocol only; forbid its claims as admission evidence |
| `verify-oidc-identity==0.4.42` | Small maintained MIT verifier, but stores a static discovery/JWK set and has no owned unknown-key refresh | Reject for this requirement |
| `auth-jwks==0.4.0` | Has TTL cache and unknown-key refresh, but requires every JWK to contain `alg`; Microsoft Entra examples omit that member | Reject as incompatible with Entra key sets |
| `idpyoidc==5.0.0` | Capable full OIDC stack, but broad beta dependency surface overlaps MSAL and changes the selected protocol owner | Do not admit in this tranche |
| Direct PyJWT or JOSE RFC glue | Cryptography works, but EMR4 would own discovery, cache, concurrency and rollover code | Reject under the maintained-component requirement |
| Replace MSAL with one full Authlib client | Coherent alternative, but changes the already selected Microsoft protocol owner and needs a separate migration decision | Defer, not fallback |

## Dependency side effects

This tranche adds three exact requirement lines and no application imports. It adds no endpoint, table, provider call, credential, identity record, session, product read, deployment or release. A future adapter must be separately authorised and must use only the frozen two-component seam.
