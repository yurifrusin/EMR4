# Stage 2 Technical Maintenance — Sol Acceptance

Date: 2026-07-19

Owner/reviewer: GPT Sol Extra High

Decision: `candidate_pass_pending_protected_integration`

## Accepted scope

Yuri explicitly authorized the non-production recommendations recorded in
`docs/bernie-stage2-technical-workflow-retrospective.md`: opt-in auto-merge
under unchanged protections, pinned Ruff developer/CI parity, a canonical
verification entry point, LF receipt normalization, historical empty-database
Alembic repair, and standardized outer timeouts.

Production database-role/GUC and field-encryption work was conditional on a
future production-planning decision and remains excluded.

## Gate disposition

| Gate | Result | Evidence |
|---|---|---|
| A1 authority | pass | User approval and fresh five-source receipts bind the exact non-production scope |
| A2 GitHub policy | pass | `allow_auto_merge=true`; protected master configuration read back unchanged |
| A3 pinned tooling | pass | Ruff 0.15.22, Bandit 1.9.4, and pip-audit 2.10.1 installed from `requirements-dev.txt` |
| A4 Ruff baseline | pass | `E9`/`F401` exact allowlist clean; 16 unused imports removed |
| A5 canonical verification | pass | fast, CI lint/security, Bandit, and migration profiles share one entry point |
| A6 receipt determinism | pass | byte writer and test prove UTF-8, terminal LF, and no CRLF |
| A7 timeout semantics | pass | centralized 120/300/900-second margins; launcher timeout exits 124 distinctly |
| A8 empty migration | pass | disposable empty up/check/down-empty/re-up/check lifecycle passes and cleans up |
| A9 preserved migration | pass | configured development DB remains at head, drift-free, and was not downgraded |
| A10 regression | pass | 60 focused tests plus 13 Stage 2 database tests, compilation, JS syntax, whitespace |
| A11 scope | pass | no Stage 3, product behavior, provider, protected evidence use, PII, production, deployment, release, or new write authority |

## Incident disposition

An exploratory Ruff baseline statically traversed sealed historical Bernie
module paths before the exact allowlist was applied. It surfaced only lint
coordinates/import names, executed nothing, and revealed no fixtures, cases,
labels, decisions, scores, hashes, or data. No reported finding from those
paths was used. The final allowlist and its regression test prevent recurrence.
The event is retained as a contained source-structure incident, not treated as
evidence and not used to broaden protected authority.

## Critical SHA-256 values

| Artifact | SHA-256 |
|---|---|
| `requirements-dev.txt` | `7868ace5ef18251915ef0fbc9c61bd1c08920d8159ec7ebb9463f23f6d7c9897` |
| `.github/workflows/python-security.yml` | `a36aab755779044cd293d511a43f28b70f1dd909f57e4fb22b461ecabd7e94eb` |
| `scripts/ariadne_orchestrator_preflight.py` | `5fb359b1eba979a0397344b8cf5261198b861abbf6220995a105080290a0854f` |
| `scripts/verification_runtime.py` | `30751884d86499ffc65ca33944b8e861691657ff4d5694cd97e11fd0f24fe813` |
| `scripts/verify_repository.py` | `80718f4270055f11a9cc620dd500f5f579cf58d58af2fb225efb48413799ea21` |
| `scripts/verify_empty_database_migrations.py` | `ac514418f77672defbf0844c28ceae4e83391d207eabdff8f01253acfb0731e9` |
| `alembic/versions/d4787e8e3629_phase_0_baseline.py` | `51d731271ab46800762cae403a02dd09e7049a1b5e21c8c747cfdec449aac326` |
| `tests/test_repository_maintenance.py` | `d3c1ab529cbf4022eebd8ab0b45444faf0fe174236dba938031c7927a948d023` |

## Integration boundary

This acceptance authorizes normal commit, push, protected PR, and opt-in squash
auto-merge after exact scope review and a passed pre-push receipt. Required
checks and conversation resolution remain mandatory; no admin bypass is
authorized. Final `technical_maintenance_pass` requires protected integration
and aligned `master`/`handoff/current` readback.
