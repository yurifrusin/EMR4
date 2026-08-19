# Threat-model delta — default-off check-in environment manifest and secret posture

Date: 2026-08-19

Scope: provider-free repository-static architecture only.

## Protected assets

- ordinary-practice admission remains absent and default-denied;
- database credentials, JWT signing material and admission verification keys;
- exact environment, practice-scope and runtime-role bindings;
- tenant isolation and future operational-evidence integrity;
- full Git-object provenance and clockwork closeout integrity; and
- product, patient, appointment, clinical and protected evidence.

## Trust boundaries

The human-authored manifest is declarative input, not authority. Typed schema
validation, exact source/Git binding, independent operational evidence and the
accepted admission evaluator are separate boundaries. A secret reference is
not secret material and a manifest assertion is not an attestation.

## Threats and controls

| Threat | Consequence | Frozen control |
|---|---|---|
| Raw secret or database URL enters a manifest | Repository or review leakage | Closed schema, recursive forbidden-field scan, reference-only slots, no local `.env` read |
| Seven-character or unresolved Git object | Ambiguous provenance | Exact lowercase `^[0-9a-f]{40}$` type plus future resolution requirement |
| Synthetic allowlist reused as ordinary environment | Accidental enablement | Separate environment/practice reference; no manifest instances or ordinary records; synthetic substitution forbidden |
| Runtime role is owner or `BYPASSRLS` | Cross-tenant access | Exact logical role, non-owner and `NOBYPASSRLS` expectations plus later independent attestation |
| One credential/key reused for several purposes | Compromise crosses boundaries | Three ordered distinct slots; duplicate reference or key identifier denies |
| Reference reused across environments | Environment boundary collapse | Exact environment binding on manifest, role and every rotation artifact; cross-environment reuse denies |
| Author marks a key “rotated” | False custody assurance | No trusted rotation Boolean; immutable independent evidence reference, digest, sequence and expiry are required |
| Stale evidence remains accepted | Compromised or retired key appears current | Exact key/version/generation binding, freshness expiry, no last-known-good fallback |
| Secret-material hash is published as proof | Offline attack or sensitive fingerprint leakage | Secret material hashes/fingerprints are forbidden; only evidence-artifact SHA-256 is allowed |
| Break glass becomes an enablement bypass | Ordinary admission without gates | Deny-only states, absence denies, no bypass/secret injection/automatic clear, new generation required for recovery |
| Manifest itself becomes activation authority | Control-plane bypass | Evaluation output is evidence-gate-only; admission state machine, feature gate and kill switch remain independently mandatory |
| Model, agent, telemetry or event asserts posture | Unreviewed authority escalation | No model/agent/event/telemetry authority; future state changes remain typed human-authorized commands |
| Multiple current manifests exist | Ambiguous environment authority | Uniqueness required; multiple current instances deny |
| YAML parser permissiveness changes meaning | Alias/type/key ambiguity | Normalization to one closed JSON reading before evaluation; unknown fields deny |
| Closeout manually copies IDs/revisions | Stale or abbreviated binding | Live single-owner clockwork derives full Git objects and canonical projections |

## STRIDE reading

- **Spoofing:** opaque references never prove possession; exact independent
  evidence and environment binding are required.
- **Tampering:** immutable digests, full Git objects, closed schemas and
  generation binding detect changed manifests or evidence.
- **Repudiation:** future role/rotation evidence requires an independent
  verifier reference; this architecture creates no audit event itself.
- **Information disclosure:** no secrets, connection URLs, provider endpoints,
  PHI, practice identifiers or raw evidence enter the contract.
- **Denial of service:** fail-closed expiry or missing evidence can block future
  admission; deny-only break glass makes that availability tradeoff explicit.
- **Elevation of privilege:** the manifest cannot activate, connect, resolve a
  secret, attest a role, clear a kill switch or execute check-in.

## Residual risks and later proof

The schema cannot prove a secret manager’s custody, a role’s real PostgreSQL
attributes, cross-tenant denial, rotation execution, unknown-commit recovery or
operator response. Those remain operational evidence. The next disposable
PostgreSQL rehearsal must use synthetic ephemeral values and must not claim
production or ordinary-practice readiness.

No product/config/API/database/client change, ordinary-practice enablement,
secret access, patient/clinical data, provider call, deployment, release,
Pages or protected-ref movement is authorized.
