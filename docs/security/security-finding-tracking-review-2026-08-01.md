# Security finding tracking review — 2026-08-01

Status: point-in-time read-only inventory; no alert disposition or GitHub
setting was changed.

## Answer

EMR4 has durable GitHub-hosted detection, but it does not yet have a complete,
owned security-finding lifecycle independent of one laptop. The laptop Codex
automation is an additional daily review, not the only scanner, but findings
from it have no mandatory ingestion path into a durable backlog.

## Controls observed

- CodeQL runs on `master` pushes, pull requests and a weekly GitHub schedule.
- Python dependency audit, Bandit and repository lint run on pushes and pull
  requests, but have no schedule.
- Node production audit and Office manifest checks run on pushes and pull
  requests, but have no schedule; the development audit is visible and
  non-blocking.
- Dependabot checks GitHub Actions, pip and npm weekly.
- GitHub secret scanning has one resolved alert and no open alert in this
  inventory.
- Private vulnerability reporting is directed through the repository Security
  tab. There is no open repository security advisory.

## Current durable backlog signals

GitHub API read at 2026-08-01:

- Dependabot: 9 open alerts, 8 high and 1 medium, all in
  `EMR4 Sidebar/package-lock.json` (alerts 5 and 8–15).
- Code scanning: 404 open alerts. Of these, 3 are security-severity high on
  `master`; the other 401 are CodeQL correctness/quality notes, warnings or
  errors without a security severity.
- Secret scanning: 0 open, 1 resolved.
- Public GitHub issues matching security/vulnerability/CVE/Dependabot/CodeQL:
  none.

The three high CodeQL instances are 295, 272 and 268. They are not newly
untriaged: all were traced in
`docs/security/codeql-high-validation-2026-07-17.md` and recorded in
`docs/security/codeql-high-validation-ledger.jsonl` as not surviving as
reportable high findings. They nevertheless remain open in GitHub, so the
source tracker and repository validation ledger have drifted.

Dependabot alert 5 has a durable, owner-approved deferment in
`docs/security/dependency-security-maintenance-2026-07-17.md`. Alerts 8–15 do
not yet have equivalent repository dispositions. A fresh local
`npm audit --omit=dev --json` reports zero production dependency
vulnerabilities; the full development graph reports 13 high and 6 moderate
vulnerable dependency nodes. This is useful reachability context, not a
dismissal decision.

The two latest published Python Security pull-request runs failed at the
reviewed Bandit baseline gate. Dependency audit and lint passed, but the branch
contained 14 findings not represented in the two-entry baseline. This review
then validated all 14 in
`docs/security/bandit-candidate-validation-2026-08-01.md`, added exact local
annotations, and reran the blocking gate successfully. The published GitHub
runs remain historical failures until a later authorised publication triggers
a new run.

## Tracking gaps

1. No single durable register joins GitHub alert ID, repository validation,
   owner, status, due date, accepted risk and final GitHub disposition.
2. New laptop-only Codex findings have no guaranteed repository/GitHub handoff.
3. Python and Node security workflows are not scheduled independently of code
   changes.
4. Existing validated CodeQL items remain open, while newer Dependabot alerts
   lack recorded validation.
5. There is no explicit triage SLA or named operational owner in
   `SECURITY.md`.

## Safe next decisions

- Validate Dependabot alerts 8–15 without force upgrades or unsupported
  overrides; the 14 Bandit candidates now have a durable validation ledger.
- Create a sanitized durable register keyed to native GitHub alert IDs and
  require every laptop finding to enter it or a private advisory.
- Decide whether Python and Node security workflows should gain a daily GitHub
  schedule, with scheduled failures assigned to an owner.
- Reconcile the already-validated CodeQL highs with GitHub only under explicit
  alert-disposition authority.
- Add ownership and response-time rules to `SECURITY.md` after review and
  explicit approval of that policy diff.

This review does not classify the new dependency or Bandit candidates as
exploitable, does not suppress them, and grants no authority to make GitHub or
dependency changes.
