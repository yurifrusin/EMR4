# Raisa two-component OIDC verifier architecture revision closeout

Date: 2026-08-02
Result: `two_component_oidc_verifier_architecture_revision_pass`

## Accepted result

The parent MSAL-only verifier claim is corrected. MSAL 1.37.0 owns Microsoft confidential-client authorization-code mechanics; Authlib 1.7.2 and JOSE RFC 1.7.4 independently own RS256 signature, JWK selection/rollover and OIDC claim admission. MSAL-decoded claims are explicitly non-authoritative.

The non-mounted callback contract now uses `response_mode=form_post`. The future verifier has an exact tenant/discovery/issuer policy, a 16 KiB raw-token limit, 60-second claim leeway, one unknown-key refresh, a 24-hour maximum verifier-client lifetime, normalized errors and no fallback. Exact package pins are admitted after licence, compatibility, distribution-hash, source-behavior and advisory review.

## Evidence

The provider-free runner passes seventeen authored-synthetic cases. It proves exact MSAL minimal scopes, S256 and form-post configuration; valid Authlib/JOSE RFC admission; denial for tampering, wrong algorithm, issuer, audience, nonce, time, tenant and identifier; valid one-refresh rollover; denial after exhausted or unavailable refresh; token-size denial; and metadata-algorithm denial.

`pip check` reports no broken requirements. `pip-audit -r requirements.txt --desc --progress-spinner off` reports no known vulnerabilities. The focused architecture, inherited parent, continuity and API-spine suite passes 64 tests. Continuity graph revision 193 and Compass map revision 174 bind the result.

The unfiltered repository suite stops during collection at the pre-existing import of removed `_BERNIE_SESSION_STORE` in `tests/test_api_spine_confirmation_family_idempotency_integration.py`; the same test import and missing application symbol are present at the 805b32e parent. This tranche neither caused nor repairs that unrelated historical barrier.

## Exact side effects

Three requirement lines were added. Architecture, API-spine, threat, hardening, dependency-review, offline evidence and continuity artifacts were added or revised. There were zero provider calls, real identities, mounted routes, database writes, sessions, product reads, deployments or releases. No application source imports MSAL or Authlib.

The concurrent user-owned `docs/branding/` directory was not modified, staged, tested or included in evidence.

## Remaining gates

The next safe candidate is a provider-free runtime adapter that implements only the frozen two-component ports and fault matrix. It requires fresh authority. Live Microsoft, real identity, binding, application sessions, product reads, deployment, production, release, protected integration and Pages remain separately closed.
