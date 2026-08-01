# Sol acceptance — Raisa maintained OIDC verifier and session bridge

Date: 2026-08-02

Decision: `pass`

Result: `raisa_maintained_oidc_verifier_session_bridge_architecture_pass`

## Review

- MSAL Python is the single future maintained tenant-specific OIDC/code-flow
  boundary; custom JWT/JOSE, arbitrary discovery and verifier fallback are
  forbidden.
- The future pre-practice resolver uses an execute-only no-login/no-bypass
  capability and a constrained non-table-owner security-definer routine with
  HMAC-only inputs, forced RLS and audit-before-return.
- The callback creates no session cookie. One 60-second digest-only grant is
  handed to the exact original origin in a no-store body message.
- Native Diary, installed Word and Word Online redeem inside their original
  cookie partitions using the same CSRF and atomic transaction contract.
- Redemption repeats binding resolution, freshly reloads internal authority,
  and commits grant consumption, session state and audit before any cookie.
- The API Spine describes future protocol/command boundaries but is not mounted;
  application routers, dependencies, database objects and runtime behavior are
  unchanged.

## Verification

- `python scripts/raisa_maintained_oidc_verifier_session_bridge_architecture_acceptance.py`
  — pass; 33/33 exact authored-synthetic cases.
- `pytest -q tests/test_raisa_maintained_oidc_verifier_session_bridge_architecture.py`
  — 14 passed.
- `ruff check` over the acceptance runner and focused tests — pass.
- `git diff --check` — pass.

The acceptance evidence records zero provider/network, real identity, database,
route, dependency, session, product/patient/clinical, cloud/IAM, deployment and
protected-ref side effects. The concurrent user-owned `docs/branding/raisa/`
directory remains untouched and excluded.

