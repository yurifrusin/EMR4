# Sol acceptance — Raisa real identity and Microsoft federation boundary

Date: 2026-08-01

Decision: `pass`

Result: `raisa_real_identity_microsoft_federation_boundary_architecture_pass`

## Review

- The boundary follows the EMR4 API Spine: future browser protocol and binding lifecycle changes are explicit REST/OpenAPI boundaries; Microsoft claims are never GraphQL or client-selected authorization authority.
- The architecture uses tenant-specific OIDC authorization code + S256 PKCE, exact issuer/audience/tenant/subject validation and maintained-library signing-key rollover behavior.
- The external identity key is immutable `tid` plus `oid`; email, domain, display name and Office signed-in state are never authority.
- Exactly one active pre-provisioned binding can release a principal candidate, only after required audit. No role, clinician link, capability, session or product data is released.
- The threat-model delta covers the new trust boundaries and preserves every live/provider/product/deployment gate.

## Verification

- `python scripts/raisa_real_identity_microsoft_federation_boundary_acceptance.py` — pass, 22/22 cases.
- `pytest -q tests/test_raisa_real_identity_microsoft_federation_boundary.py` — 10 passed.
- `ruff check scripts/raisa_real_identity_microsoft_federation_boundary_acceptance.py tests/test_raisa_real_identity_microsoft_federation_boundary.py` — pass.

No external worker, provider, Microsoft, database, product or deployment action occurred.
