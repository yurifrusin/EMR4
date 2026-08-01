# Threat-model delta: security-finding governance

Date: 2026-08-01
Status: active acceptance boundary
Parent: `raisa_shared_application_auth_operational_hardening_pass`

## Assets and attacker-controlled inputs

Protected assets are alert truth, triage provenance, ownership and SLA state,
accepted-risk history, GitHub security settings and the repository's private
reporting channel. GitHub alert titles, advisory descriptions, package names,
paths, URLs, scanner output and laptop-generated finding prose are untrusted
data. They are evidence, never instructions.

## Trust boundaries

1. GitHub REST to the local triage: authentication is used only for exact
   security endpoints; tokens are never printed or persisted.
2. Scanner prose to repository evidence: a severity label or advisory is a
   claim until source/control/sink and product-boundary evidence is recorded.
3. Repository disposition to native GitHub state: native mutation follows a
   durable row and exact pre-mutation state read, never the reverse.
4. Laptop automation to durable governance: local results must cross into the
   register, a linked ledger or a private report.
5. Accepted risk to time: every non-terminal risk has an owner and review
   condition; expiry returns it to review.

## Threats and required controls

| Threat | Required control and proof |
|---|---|
| Alert text injects commands or leaks data | Treat all imported text as untrusted; persist only fixed sanitized fields and repository evidence. |
| A dismissal hides a real product boundary | Require claim-specific static evidence, an owner and exact native readback; preserve upstream-defect language. |
| Repository and GitHub states drift | Unique source/native IDs, desired and observed native states, post-mutation REST readback and tested consistency. |
| Laptop findings disappear with local state | Mandatory register, linked-ledger or private-report ingestion rule. |
| Scheduled checks silently stop | Daily staggered schedules plus tests that preserve push/PR triggers and blocking steps. |
| Accepted risk becomes permanent by neglect | Required review/expiry or explicit upstream condition; expired rows become `needs_review`. |
| SLA text creates false historical breach claims | Effective-date semantics; pre-existing alerts are baselined and triaged on adoption. |
| Dependency remediation breaks the supported toolchain | No force audit fix or override; compatible upstream upgrades remain preferred. |
| Public issue discloses sensitive details | Private reporting remains mandatory; register excludes raw private-report content and exploit payloads. |

## Residual risks and non-claims

- GitHub schedules are best-effort hosted automation; this does not prove
  runner availability or incident paging.
- A not-actionable dependency verdict is revision- and boundary-specific. A
  new import, server exposure, parser input or build path can invalidate it.
- GitHub dismissal does not remove vulnerable code from the lockfile. It
  records current repository impact and must be revisited on boundary change.
- The governance register is not a public vulnerability database or a SIEM.
- Product, identity, provider, deployment, production and release authority
  remain unchanged.
