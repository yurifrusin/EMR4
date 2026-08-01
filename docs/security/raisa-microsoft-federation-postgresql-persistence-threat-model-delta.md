# Threat-model delta: Raisa Microsoft-federation PostgreSQL persistence

Date: 2026-08-01

Parent: `docs/security/raisa-microsoft-federation-admission-runtime-threat-model-delta.md`

Scope: Route-free authored-synthetic binding and audit persistence in a disposable local PostgreSQL database.

## New assets and boundaries

- uniqueness and lifecycle state of external-identity bindings;
- keyed external/correlation references;
- injected synthetic HMAC key boundary;
- append-only admission/lifecycle audit;
- PostgreSQL transaction, row lock, constraints, triggers and RLS policy; and
- migration downgrade and cleanup integrity.

## Threats and controls

| Threat | Control | Residual boundary |
|---|---|---|
| Raw external identifier leaks through schema/log/audit | no raw columns; versioned keyed HMAC; row scan; no URL/name in evidence | production logging, backup and key custody review |
| Plain hash permits enumeration | minimum 256-bit injected HMAC key | KMS/HSM storage, rotation and dual-read migration |
| Two administrators bind one subject concurrently | database composite uniqueness; independent-session concurrency test | live command idempotency and human authorization |
| Binding is silently reassigned | immutable identity/principal columns; only terminal revoke transition | separate audited replacement/recovery command |
| Revoked binding is reactivated | trigger rejects any update after revoke and any transition other than active-to-revoked `version + 1` | restoration policy deliberately absent |
| State commits without audit | binding create/revoke and lookup audit share transaction; forced audit failure rolls back mutation | later session bridge cross-boundary atomicity |
| Audit is rewritten | append-only trigger rejects update/delete | retention/export/SIEM and privileged DBA controls |
| Cross-practice read | forced RLS and exact practice policy; disposable no-bypass role probe | provider-to-practice bootstrap role remains unresolved |
| Table owner bypass becomes production posture | no durable role or grant; owner-only proof is explicitly non-production | least-privilege resolver/audit ingress design later |
| Migration targets shared data | loopback/port/source guard; unique allowlisted database name; exact create/drop | CI environment credential governance |
| Synthetic module is routed | router-import and forbidden-client static tests | release/build configuration gate |

## Privacy boundary

The database is structurally incapable of storing raw Microsoft tenant/object/subject identifiers, email, name, token or authorization code in these tables. Synthetic internal user/practice references remain identifiable only inside the authored-synthetic fixture. Production data classification, retention, subject access, deletion, breach response and backup disposal remain unresolved.

## Closed gates

Live identity, Microsoft/provider network, real secret/key custody, public routes, cookies, session creation, product identity reload, product reads, durable runtime roles, cloud/IAM changes, deployment, production and release remain closed.

---
Reviewed-by: Codex Security threat-model workflow
Review-date: 2026-08-01
Repository: EMR4
Version: e201435a
