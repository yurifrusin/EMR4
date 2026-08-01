# EMR4 security-finding governance closeout

Date: 2026-08-01

Result: `security_finding_governance_pass`

## Outcome

The separately authorised repository-local security-finding-governance
descendant passes. EMR4 now has one sanitized, schema-validated register that
joins 12 native GitHub alerts to an owner, severity, acknowledgement and triage
times, evidence, repository verdict, exact native disposition, review date,
expiry and reopening condition. The register also links the existing 14-row
Bandit and 10-row CodeQL instance-preserving validation ledgers.

This closes the laptop-only tracking gap. A local Codex result is now
supplementary evidence rather than a durable disposition by itself.

## Native alert reconciliation

Fresh GitHub REST reads preceded every disposition and a second exact readback
followed them. The final native state matches the register:

- Dependabot alerts 5 and 8-15 are dismissed. Alerts 9, 11 and 12 use
  `not_used`; the other six use `tolerable_risk`.
- CodeQL alerts 295, 272 and 268 are dismissed as `false_positive` after their
  prior instance-preserving validation defeated the claimed security impact.
- The reconciled queues contain zero open Dependabot alerts and zero open
  security-high CodeQL alerts.

The eight newly triaged dependency advisories remain genuine upstream defects.
Every affected resolution is development-only at this revision, and the exact
supported repository path either does not call the advisory sink or supplies
only trusted local developer configuration. The vulnerable lockfile entries
were not removed, overridden or force-upgraded. Compatible upstream toolchain
updates remain preferred and every disposition has a bounded review condition.

The mutation history is preserved in the native evidence. An initial
Dependabot PowerShell interpolation error received HTTP 422 for all nine
requests and changed nothing. The first CodeQL batch applied the correct state
and reason but an incorrect literal comment; each exact alert was then reopened
and immediately redismissed with the unchanged verdict and correct evidence
comment. The final state, reason, timestamp and comment readback all match the
durable rows. GitHub renders the CodeQL reason as `false positive`; the
register and evidence use the API-safe normalized enum `false_positive`.

## Repository policy and automation

The approved root `SECURITY.md` now names `@yurifrusin` as security maintainer,
requires register, linked-ledger or private-report ingestion, defines response
targets by severity, requires owner/evidence/review/expiry for accepted risk,
and makes expired dispositions return to review.

The existing blocking Python and Node security workflows preserve their push
and pull-request triggers and now define staggered daily schedules:

- Python: `17 18 * * *` UTC;
- Node and Office add-in: `47 18 * * *` UTC.

GitHub scheduled workflows run from the default branch. These definitions are
therefore repository evidence only until the draft PR passes protected review
and is integrated into `master`; this result does not claim that a scheduled
run has already executed.

## Acceptance evidence

The deterministic acceptance runner validates the register schema, unique
native inventory, owner and SLA fields, exact native evidence, linked-ledger
row counts, schedules, preserved blocking gates and approved policy markers.
Its recorded result is `security_finding_governance_pass`.

All 183 selected serial cross-checkpoint cases pass across shared-auth
transport, operational hardening, persistence/runtime foundations, API Spine,
security tooling, governance, Word companion continuity, Compass and handover
integrity. Ruff, the reviewed Bandit baseline, pip-audit, the blocking
production npm audit, Office manifest validation, structured register
validation and `git diff --check` pass.

No protected holdout or raw historical Diary material was inspected. No
product or patient/clinical data was read; no provider was called; and no
identity, cloud/IAM, deployment, production or release state changed. Native
alert disposition is the only external mutation in this descendant.

## Worker and publication disposition

GPT-5.6 Luna was not exposed by the current subagent interface. No substitute
subagent, external worker, provider or independent external reviewer ran; the
tightly coupled register, policy, REST reconciliation and acceptance remained
under one Sol owner.

Yuri separately authorised one intentional commit, push of the existing task
branch and a draft pull request for the complete cross-checkpoint result.
`master`, `handoff/current` and all other protected refs remain outside that
authority and must not move during this closeout.

## Claim limit and next candidate

This pass proves durable repository governance, exact point-in-time native
alert reconciliation and daily workflow definitions. It does not prove hosted
runner availability, default-branch schedule activation, incident paging,
SIEM, removal of the development-only vulnerable resolutions, real identity,
product-data safety, deployment, production fitness or release readiness.

The leading next candidate is one supervised, authored-synthetic Office
cookie-compatibility exercise. It requires fresh authority; real identity,
Microsoft/Office federation authority and every product read remain closed.
