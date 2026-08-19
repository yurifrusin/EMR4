# Threat-model delta — disposable PostgreSQL check-in runtime role and tenant isolation attestation

Date: 2026-08-19

Timestamp: 2026-08-19T15:57:14.2434422+10:00 (Australia/Brisbane)

Scope: one provider-free uniquely named disposable local PostgreSQL 16
attestation using authored-synthetic identifiers only.

## Boundary classification

This is an API Spine manifest/capability evidence rehearsal. The in-memory
manifest is declarative input and never a command, executable policy engine,
ordinary-admission grant or database credential. PostgreSQL catalogue and RLS
behavior are the enforcing and attesting boundaries. No REST/OpenAPI command,
GraphQL read/mutation, async event, audit record or idempotency receipt is
created.

## Protected assets

- ordinary-practice check-in remains absent and default-denied;
- exact tenant separation and future runtime-role least privilege;
- live secrets, existing databases and product relations;
- product, patient, appointment, clinical and protected evidence;
- full Git-object provenance and sanitized evidence integrity; and
- host Docker resources, loopback transport and exact cleanup authority.

## Trust boundaries

The manifest author does not attest the role. The dynamic role cannot attest
itself. Admin catalogue queries, application-role behavioral checks and
captured-ID cleanup are distinct. Docker names, raw output, manifest assertions
and evidence paths are untrusted until typed validation and exact digest checks
pass.

## Threats and controls

| Threat | Consequence | Frozen control |
|---|---|---|
| Existing or hosted database is selected | Product/operational data exposure | Exact cached-image disposable-container profile; no host mount, `.env`, external DSN or fallback |
| Container or network name is reused for cleanup | Unrelated resource removal | Random nonce plus labels; cleanup targets captured exact IDs only after ownership and empty-network reverification |
| Image pull or published port opens egress/exposure | Unbounded external dependency or host exposure | Pull policy `never`, internal network, no published port, loopback relay only |
| Password enters contract/evidence/log | Credential leakage | 32-byte process-memory value, no raw output, closed schemas and recursive forbidden-value scanner |
| Manifest reference is treated as secret possession | False custody claim | Reference-only fixture; actual password is distinct and never serialized; rotation/custody remains unproved |
| Role owns a relation or bypasses RLS | Tenant escape | Catalogue assertions for all role flags, memberships and zero ownership; admin owns forced-RLS probe |
| Universal denial is mistaken for isolation | False-positive proof | Same-tenant select/insert/update must succeed before cross-tenant denials count |
| Select-only test misses write escape | Cross-tenant mutation | Explicit insert SQLSTATE `42501` plus update/delete zero-row checks |
| Session tenant setting leaks | Later transaction inherits tenant | `SET LOCAL` only; absent-setting zero visibility and post-transaction absence checks |
| Role escalates with membership or `SET ROLE` | Admin access | No memberships; exact admin `SET ROLE` denial with SQLSTATE `42501` |
| Probe is confused with product behavior | Overclaim | Dedicated non-product schema/table, zero app imports, strict evidence label and claim boundary |
| Role remains after evidence | Persistent capability | Explicit role drop/absence before container teardown, then captured-ID container/network absence |
| Failure evidence preserves raw SQL/output | Secret or environment disclosure | Stage/reason/class/SQLSTATE allowlist only; no raw exception or command output |
| Synthetic attestation activates ordinary practice | Authority escalation | Canonical manifest/admission/release counts remain zero; no evaluator release, product config or command path |
| Seven-character Git object enters evidence | Ambiguous provenance | Full lowercase 40-character schema and mechanically resolved source checks |

## STRIDE reading

- **Spoofing:** role identity is checked through `current_user` and `pg_roles`,
  not a caller label.
- **Tampering:** exact source hashes, closed schemas, manifest and attestation
  digests, and catalogue facts fail closed.
- **Repudiation:** parent evidence binds the separate attestation artifact and
  exact scenario results; this remains rehearsal evidence, not product audit.
- **Information disclosure:** no PHI, product row, live secret, DSN, Docker
  environment or raw output is retained.
- **Denial of service:** strict cleanup can reject an otherwise successful run;
  that availability tradeoff is accepted for fail-closed evidence.
- **Elevation of privilege:** negative role attributes, zero ownership,
  memberships, forced RLS and `SET ROLE` denial are all independently checked.

## Residual risks and later proof

This rehearsal cannot prove live secret custody/rotation, a real practice
environment, product-schema grants, production RLS coverage, operator response,
rollback or unknown-commit recovery. It deliberately grants DML only on one
synthetic probe and produces no command audit/idempotency evidence. The later
rollback/unknown-commit tranche remains mandatory before any ordinary-practice
admission decision.

No product/config/API/client change, ordinary-practice enablement, secret
access, product/patient/clinical data, provider call, occupied DeepSeek HMR,
deployment, release, Pages or protected-ref movement is authorized.
