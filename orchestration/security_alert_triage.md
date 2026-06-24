# EMR4 Security Alert Triage

Sprint 21 turns the Sprint 20 GitHub security baseline into a concrete alert
triage pass. This report is Ariadne-owned because the Codex worker repeatedly
hit local tooling issues after plan approval; no secrets are committed here.

## Snapshot

| Item | Value |
|---|---|
| Captured | 2026-06-24 |
| Source | GitHub Security APIs via `gh` |
| CodeQL open alerts | 43 after Sprint 21 CodeQL rerun |
| CodeQL high alerts | 3 after Sprint 21 CodeQL rerun |
| CodeQL medium alerts | 0 after Sprint 21 CodeQL rerun |
| Dependabot open alerts | 7 npm devDependency/build-tool alerts after GitHub advisory refresh |
| Secret scanning open alerts | 0 |
| Secret scanning resolved alerts | 1 |

## Fix Now In Sprint 21

| Alert(s) | Rule | Path | Owner | Status |
|---|---|---|---|---|
| 12, 13 | `py/clear-text-logging-sensitive-data` | `app/routers/consultation.py` | Claude + Ariadne repair | Addressed by logging counts and exception classes only |
| 14, 15 | `py/path-injection` | `app/routers/consultation.py` | Claude | Addressed by bounded audio cleanup under `static/audio` |
| 7, 8 | `py/stack-trace-exposure` | `app/routers/consultation.py` | Claude + Ariadne repair | Addressed by generic client errors |
| 16 | `py/empty-except` | `app/routers/consultation.py` | Claude | Addressed by bounded malformed-JSON logging |
| Node dev audit | `form-data`, `hono`, `http-proxy-middleware` | `EMR4 Sidebar/package-lock.json` | Antigravity | Addressed by non-breaking lockfile updates |

GitHub re-ran CodeQL on the integrated `master` commit and the targeted
consultation alerts are no longer open.

## Defer

| Alert(s) | Rule | Path | Rationale |
|---|---|---|---|
| 9, 10, 11 | `py/clear-text-logging-sensitive-data` | `scripts/audit_patient_duplicates.py` | Real but scoped to a dev/admin duplicate-audit script; should be a separate small hardening task so this sprint stays focused |
| 1-6 | `js/automatic-semicolon-insertion` | `EMR4 Sidebar/src/taskpane/taskpane.js`, `docs/taskpane/taskpane.js` | Note-level JavaScript style/safety signal; should be handled in a frontend hygiene slice with source and deployed copy kept in sync |
| 17-50 except 38 | unused imports/globals/local variables | app, tests, migrations | Note-level hygiene; batch later to avoid noisy sprint scope |
| 38 | unused local variable | `app/routers/consultation.py` | Note-level pre-existing cleanup; not security-critical for Sprint 21 |

## Post-Closeout Follow-Up

| Alert(s) | Rule / Signal | Status |
|---|---|---|
| 9, 10, 11 | `py/clear-text-logging-sensitive-data` in `scripts/audit_patient_duplicates.py` | Addressed locally by redacting default report output and raw exception text; pending GitHub CodeQL confirmation after push |
| 1-6 | `js/automatic-semicolon-insertion` in taskpane source/deployed copies | Addressed locally with explicit semicolons and taskpane JS cache-bust `v=57`; pending GitHub CodeQL confirmation after push |
| Dependabot 1-7 | npm devDependency/build-tool advisories | Partially addressed with safe `copy-webpack-plugin` / `webpack-dev-server` updates and non-forced `npm audit fix`; remaining full-audit signal is 11 moderate `uuid` transitive findings in Office add-in tooling |

## Dependency Signals

- `npm audit --omit=dev` remains clean after Antigravity's package-lock update.
- Full `npm audit` now reports 11 moderate devDependency/build-tool issues in
  `uuid` through Office add-in tooling.
- `npm audit fix --force` would take a breaking `office-addin-manifest@1.0.0`
  path, so the remaining issue is not auto-fixed in the routine safe-fix lane.
- These remaining issues are not production runtime dependencies and require
  a dedicated toolchain-modernization decision if they persist after GitHub
  recalculates Dependabot alerts.

## Secret Scanning

- Secret scanning has no open alerts.
- The previously observed GCP API key alert is resolved as `revoked`.
- No secret values were queried into this report or committed.

## Recommended Follow-Up

1. Re-check GitHub CodeQL and Dependabot after the follow-up commit lands.
2. Keep forced Office add-in tooling major/devDependency upgrades deferred until they
   can be tested as a dedicated build-tool modernization sprint.
