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

## Dependency Signals

- `npm audit --omit=dev` remains clean after Antigravity's package-lock update.
- Full `npm audit` still reports devDependency/build-tool issues in
  `serialize-javascript` and `uuid` through older build tooling.
- GitHub Dependabot now also reports open devDependency/build-tool advisories,
  including `webpack-dev-server`.
- Those remaining issues are not production runtime dependencies and require
  higher-risk major upgrades, so they are deferred.

## Secret Scanning

- Secret scanning has no open alerts.
- The previously observed GCP API key alert is resolved as `revoked`.
- No secret values were queried into this report or committed.

## Recommended Follow-Up

1. Plan a small dev-script hygiene task for `scripts/audit_patient_duplicates.py`
   to remove clear-text patient duplicate logging or gate it behind explicit
   redaction/output options.
2. Plan a frontend hygiene task to resolve JavaScript automatic-semicolon
   insertion notes in both source and deployed taskpane copies.
3. Keep forced Office/webpack major devDependency upgrades deferred until they
   can be tested as a dedicated build-tool modernization sprint.
