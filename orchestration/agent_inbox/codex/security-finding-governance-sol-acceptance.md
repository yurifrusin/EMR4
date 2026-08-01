# Sol acceptance — EMR4 security-finding governance

Date: 2026-08-01

Decision: `accepted`

Result: `security_finding_governance_pass`

Coordinates after closeout: Continuity graph revision 186 / Compass map
revision 167, sourced from graph revision 186.

## Independent evidence review

Sol reviewed the frozen plan and threat delta, the schema and all 12 sanitized
register rows, eight-alert Dependabot static trace, approved root security
policy, both workflow definitions, exact native disposition evidence and the
deterministic acceptance output without relying on the runner's final boolean.
The evidence establishes:

- every governed native ID is unique and has an owner, time-bound triage and
  review state, repository evidence and exact desired/observed native state;
- Dependabot alerts 8-15 describe upstream defects but do not cross the
  supported EMR4 product/runtime boundary at this revision;
- the three named CodeQL highs retain their prior instance-preserving false-
  positive evidence;
- all 12 final GitHub states, reasons, timestamps and comments match the
  register, with zero open alerts in the reconciled Dependabot and
  security-high CodeQL queues;
- the 14 Bandit and 10 CodeQL validation rows remain durably linked; and
- the security workflows retain push/PR and blocking gates while adding two
  distinct daily schedules.

The root-policy resolver selects the approved `SECURITY.md`. Its owner, SLA,
laptop-ingestion and accepted-risk expiry requirements match the frozen plan.

All 183 selected serial cross-checkpoint tests pass. Ruff, the reviewed Bandit
baseline, pip-audit, the blocking production npm audit, Office manifest
validation, register-schema validation and whitespace checks also pass.

## Veto and non-claims

Acceptance is vetoed from being described as dependency remediation, proof of
a completed scheduled run, hosted-runner or incident-response availability,
SIEM, product security certification, deployment, production or release.
Default-branch schedule activation awaits protected integration. The affected
development dependency resolutions remain and must be revisited on a boundary
change or compatible upstream remediation.

Protected holdouts and raw historical Diary material remain unopened. No
product/patient/clinical data, external identity, provider, cloud/IAM,
deployment or production state was accessed or changed. No Luna or substitute
worker ran. Publication is limited to the user-authorised task-branch commit,
push and draft PR; protected refs remain unchanged.
