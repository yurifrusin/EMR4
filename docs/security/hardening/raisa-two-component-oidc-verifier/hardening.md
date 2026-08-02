# OIDC identity-admission hardening portfolio

## Executive summary

We found a structural contradiction: the selected Microsoft protocol client decodes ID-token claims but does not verify their JWS signature. The parent design therefore cannot safely assign signature, key-cache and rollover ownership to MSAL. We recommend retaining MSAL for the flow and adding a narrowly exposed Authlib/JOSE RFC verification component.

The selected option is `msal-authlib-verifier`. It produces the smallest controlled correction, preserves the chosen protocol client, removes custom key-handling pressure, and gives unknown-key rollover one maintained library-owned retry. This architecture admission and package review do not implement the runtime boundary.

## Evidence-backed opportunity

The diagnostic and MSAL source establish the missing verification property (E004, E005). Microsoft requires signature, issuer, audience and time validation and describes signing-key rollover (E008, E009). Authlib source demonstrates maintained JWS validation, OIDC claim checks and one forced JWKS refresh on unknown `kid` (E006, E007, E010).

## Options

| Option | Security | Performance | Memory | Reliability | Operability | Migration |
|---|---|---|---|---|---|---|
| `tls-only-msal` | Fails the required independent signature property | Lowest local work | Lowest | Depends entirely on token-endpoint/TLS context | Simple but misleading | No change |
| `msal-authlib-verifier` | Independent RS256 and OIDC claim admission; no fallback | One local verify; network only for metadata/key refresh | One bounded metadata/JWK cache | One unknown-key refresh, then deny | Two packages/one seam to monitor | Small adapter change; recommended |
| `single-full-oidc-client` | Can provide coherent verification | Similar flow cost | One client cache | Mature implementation possible | One component but new protocol owner | Replaces MSAL decision and retests flow |
| `custom-pyjwt-jwks` | Safety depends on EMR4 cache/rollover/parser code | Potentially lean | Custom bounded cache | Highest edge-case burden | High bespoke maintenance | Moderate code and long-term ownership |

## Recommendation

We select `msal-authlib-verifier`. We pin MSAL 1.37.0, Authlib 1.7.2 and JOSE RFC 1.7.4, freeze their ownership contract, and require an offline acceptance harness before an application adapter is authorised. We reject the baseline because it lacks the security property and the custom option because it recreates security-sensitive protocol machinery. A single full client remains a valid future migration only if we deliberately replace MSAL.

## Evidence coverage and limits

All material claims map to E001-E010 in `context.md`. Coverage includes protocol ownership, signature verification, discovery/JWKS behavior, package metadata, licences, hashes and published advisory floors. It does not include live Microsoft behavior, tenant configuration, real identity, Office cookie compatibility, production load or incident response.
