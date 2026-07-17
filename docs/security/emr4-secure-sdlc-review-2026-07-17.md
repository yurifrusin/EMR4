# EMR4 Secure SDLC Review — 2026-07-17

## Overall assessment

EMR4 is already security-aware by design, but it is not yet doing everything
reasonably available for a healthcare system. The strongest controls are its
authority boundaries: backend ownership of clinical/diary truth, default-deny
permission design, proposal/confirmation separation, audit/idempotency
contracts, PHI transmission restrictions, blocked provider/write gates, and
fail-closed evaluation provenance.

The principal weakness is that these controls are not yet joined into one
enforced lifecycle. Detection exists, but `master` is unprotected; GitHub
secret scanning is enabled, but push protection is not; CodeQL is running, but
ten open alerts are currently classified high and have not yet received a
documented reachability/validity decision. These are governance and response
gaps, not evidence that the LC4V10 result was poor.

## Lifecycle control map

| Phase | Observed controls | Required next maturity step |
| --- | --- | --- |
| Requirements | User decision gates; PHI and provider restrictions; bounded product authority | Add a threat-model/privacy delta and misuse cases to every material sprint contract |
| Design | API Spine ADR; GraphQL read/REST command split; ABAC permission matrix; proposal/confirmation contracts | Make security architecture review a required acceptance field for trust-boundary changes |
| Implementation | Fail-closed configuration; CORS allowlist; typed contracts; worker authority isolation | Add secure-coding checks for secrets, cryptography, logging, URL/DOM sinks, and authentication changes |
| Verification | Pytest security contracts; CodeQL; Bandit; pip/npm audit; PHI leakage lint; holdout isolation | Triage high alerts to an SLA; add targeted browser/DAST and property/fuzz tests for exposed parsers and command boundaries |
| Release | Frozen acceptance artifacts; hashes; preservation gates; protected-ref protocol in project process | Enforce required checks and reviewed integration technically on `master`; produce SBOM/provenance for release candidates |
| Operations | Audit and idempotency design; default-deny authority model | Define security telemetry, alert ownership, vulnerability SLAs, incident playbooks, key rotation, backup/restore security tests, and breach exercises |
| Retirement | Historical-diary local-only and no-runtime-use boundaries | Define retention, deletion, legal-hold, credential/key revocation, and data-export verification |

## Existing strengths to preserve

- The native backend, not the LLM or UI, owns identity, availability,
  collision checks, status transitions, confirmations, writes, and audit.
- T3/provider execution and sensitive-data transmission fail closed.
- API changes have a stewarded contract, permission matrix, and deterministic
  artifact tests.
- Historical diary material is segregated, ignored, linted, and prohibited
  from external-provider use.
- Python, Node production dependencies, CodeQL, Bandit, Dependabot, and secret
  scanning are present rather than deferred to a future compliance phase.
- Evaluation artifacts preserve provenance and prevent test-set tuning.

## Priority gaps

1. **Alert response:** validate the ten high CodeQL alerts. The smoke/dev URL
   switches in the published Diary deserve first attention because they can
   alter client-side authentication flow; backend authorization must be proven
   rather than assumed. The two diagnostic-script logging findings may be safe
   aggregates, but require explicit data-classification evidence.
2. **Protected integration:** decide whether to enable branch protection with
   required security checks and review, and secret-scanning push protection.
3. **Data-plane controls:** implement PostgreSQL RLS, comprehensive append-only
   audit, field-level encryption for sensitive identifiers, and hardened JWT
   storage/rotation before production authority expands.
4. **Abuse resistance:** add rate limiting, anti-enumeration, CSRF/XSS review,
   and privacy impact assessment before patient/kiosk/external identity flows.
5. **Response readiness:** create vulnerability ownership/SLAs, disclosure and
   incident-response procedures, recovery exercises, and security metrics.
6. **Supply chain:** retain blocking production SCA, then add release SBOM and
   provenance and progressively pin third-party Actions by immutable commit.

## Recommended operating rule

Every material sprint should carry a small security delta: assets/data
touched, trust boundaries changed, attacker-controlled inputs, dangerous
capabilities added, abuse cases, required controls, verification evidence,
residual risk owner, and whether an independent security review is required.
No change should claim “security complete”; it should show which invariants it
preserves and which risks remain accepted, deferred, or blocked.

The companion hardening portfolio under
`docs/security/secure-sdlc-hardening/` compares keeping the present advisory
model with enforcing a protected delivery control plane. It is a design
proposal, not proof that the proposed GitHub settings or structural controls
have been implemented.
