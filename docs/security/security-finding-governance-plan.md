# EMR4 security-finding governance plan

Status: frozen implementation and acceptance contract
Authority: Yuri, 2026-08-01
Parent result: `raisa_shared_application_auth_operational_hardening_pass`
Parent coordinates: Continuity 185 / Compass 166

## Decision and purpose

This repository-local descendant makes EMR4 security tracking independent of
one laptop. It may:

1. maintain one sanitized, schema-validated register that joins scanner or
   native alert IDs to evidence, owner, severity, status, SLA, risk review and
   native disposition;
2. add staggered daily GitHub schedules to the existing blocking Python and
   Node production-security workflows;
3. statically triage Dependabot alerts 8-15 without force upgrades or
   dependency overrides;
4. reconcile the nine Dependabot alerts and three previously validated CodeQL
   high alerts with GitHub after the matching durable register rows exist;
5. add repository security ownership, response-time and accepted-risk rules to
   `SECURITY.md`; and
6. publish the complete intentional cross-checkpoint result from the current
   task branch as one commit and draft pull request.

## Closed boundaries

- Protected holdouts and raw historical Diary material remain sealed.
- No force dependency update, transitive override or unsupported package
  substitution is permitted.
- A native alert may change only after an exact current REST read and a
  durable evidence-backed row. A dismissal is not a claim that an upstream
  defect does not exist.
- Real identity, external federation, product-derived or patient/clinical
  data, providers, cloud/IAM resources, deployment and production remain
  closed.
- `master`, `handoff/current` and every protected ref remain unchanged.

## Governance contract

### Durable register

`docs/security/security-finding-register.json` is the sanitized index. Its
schema is `docs/security/security-finding-register.schema.json`. Every native
finding row must contain a stable local ID, source and native ID, severity,
owner, first-observed time, triage verdict, due/review dates, repository
evidence, native state and final native disposition. Local scanner results may
be represented by an immutable, instance-preserving validation ledger, but the
register must name that ledger, its exact row count and its disposition.

The register contains no tokens, request headers, credentials, patient data,
raw scanner payloads, exploit payloads or private-report content. GitHub URLs,
package names, repository paths and fixed classifications are permitted.

### Ownership and service levels

The security maintainer is `@yurifrusin`; a delegated owner may be named on an
individual row. From this policy's effective date, acknowledgement and initial
triage targets are:

| Severity | Acknowledge | Initial triage | Remediate, mitigate or accept risk |
|---|---:|---:|---:|
| Critical | 1 calendar day | 2 calendar days | 7 calendar days |
| High | 2 calendar days | 5 calendar days | 30 calendar days |
| Medium | 5 calendar days | 14 calendar days | 60 calendar days |
| Low | 10 calendar days | 30 calendar days | 90 calendar days |

Scheduled workflow failures must receive a register row or link to an existing
row within two business days. An accepted-risk or not-actionable disposition
must name the evidence, owner, rationale, review date and expiry or explicit
upstream-remediation condition. Expired dispositions return to `needs_review`.

### Laptop automation ingestion

The daily Codex check is supplementary. Every plausible finding it produces
must enter the register, an instance-preserving linked validation ledger, or a
private GitHub vulnerability report before it is treated as tracked. A local
conversation or machine-only output is not durable disposition evidence.

### Native disposition

- Dependabot dismissal reasons may be `not_used` or `tolerable_risk` only when
  the matching row establishes that the affected code is absent from the
  supported boundary or that the owner accepts a bounded residual risk.
- CodeQL dismissal may use `false_positive` only when instance-preserving
  validation defeats the query's claimed security consequence.
- Comments must cite repository evidence and must not include secrets, raw
  payloads or sensitive vulnerability detail.
- Reopening, fixing or superseding an alert requires a new register revision;
  history is not deleted.

## Frozen triage result

Dependabot alerts 8-15 are genuine upstream dependency defects but do not
survive as actionable EMR4 findings at the required starting revision. Every
affected package is `dev: true`. Exact static tracing shows either no call to
the advisory sink or only trusted local developer configuration with no
supported product/runtime boundary. Production npm dependencies remain
`core-js` and `regenerator-runtime`; the blocking production audit remains the
release-relevant gate.

This disposition does not prohibit compatible upstream upgrades. It prohibits
claiming that a force override is safer than the supported Office toolchain.

## Acceptance gates

- The Python and Node workflows have valid, distinct daily cron schedules and
  retain their existing push/pull-request triggers and blocking gates.
- The register and schema validate; every named native alert is unique and has
  complete owner/SLA/evidence/native-disposition fields.
- Dependabot alerts 5 and 8-15 and CodeQL alerts 295, 272 and 268 have exact
  current-state readback matching the register after disposition.
- The 14 Bandit candidates remain linked to their instance-preserving ledger
  and exact gate result.
- `SECURITY.md` resolves as the root policy and contains the approved owner,
  response-time, ingestion and accepted-risk rules.
- Focused governance tests, security workflows, existing security tooling
  contract tests, structured-data checks and whitespace checks pass.
- A preacceptance five-source receipt and independent Sol evidence review pass
  before the result is described as accepted.
- Publication is limited to the current task branch, one intentional commit
  and a draft PR; protected refs do not move.

Until every gate passes, the only truthful result is
`security_finding_governance_in_progress`.
