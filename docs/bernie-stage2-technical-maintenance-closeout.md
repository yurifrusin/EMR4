# Bernie Stage 2 Technical Maintenance Closeout

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision: `technical_maintenance_pass`

## Outcome

Yuri's approved non-production Stage 2 maintenance recommendations are
implemented without reopening Stage 2 product acceptance or starting Stage 3.

- GitHub auto-merge is enabled as an opt-in per pull request. The strict four
  required checks, current-head requirement, conversation resolution, admin
  enforcement, linear history, and force-push/deletion prohibitions are
  unchanged. Squash remains the intended merge method after Sol acceptance.
- `requirements-dev.txt` pins Ruff 0.15.22, Bandit 1.9.4, and pip-audit 2.10.1.
  CI and local verification use the same dependency source and commands.
- Ruff begins with only `E9` and `F401` on an explicit ordinary
  product/infrastructure allowlist. Sixteen genuine unused imports were removed
  with no behavior change.
- `scripts/verify_repository.py` is the canonical verification entry point;
  `scripts/check_backend.ps1` delegates to it.
- `scripts/verification_runtime.py` supplies risk-proportional timeouts and
  distinguishes `launcher_timeout` exit 124 from child test/tool failures.
- Ariadne receipt files are written as canonical UTF-8 LF bytes on Windows and
  CI, with a byte-level test.
- the historical root Alembic revision now bootstraps its exact legacy table
  prerequisites on a genuinely empty PostgreSQL database, refuses ambiguous
  partial legacy schemas, handles PostgreSQL-assigned foreign-key names during
  downgrade, and returns an empty bootstrap to no user tables.
- two later fresh-install schema declarations were reconciled with the existing
  ORM/development contract so a new database and the preserved development
  database both report zero model drift.

The production database-role/GUC and field-encryption recommendation remains
deferred to production planning. No production role, key, PII, provider,
deployment, release, Stage 3, event runtime, new mutation, or product behavior
authority moved.

## Verification

- canonical fast profile: pass;
- Ruff exact allowlist: pass;
- Python compilation: pass;
- focused API Spine, handover, receipt, and maintenance population: 60 passed;
- Stage 2 durable session/recovery/database population: 13 passed;
- preserved `gp_pms_dev`: Alembic head `m2n3o4p5q6r7`, no new upgrade
  operations detected, and no downgrade performed;
- disposable empty database: upgrade to head, `alembic check`, downgrade to
  base/no user tables, re-upgrade to head, and second `alembic check` all pass;
- disposable database removed in the verifier cleanup path;
- `node --check docs/diary/diary.js`: pass; and
- `git diff --check`: pass.

Protected PR 43 passed Python Security, both CodeQL language analyses, the
aggregate CodeQL context, and the Node/Office manifest/security context on exact
branch head `8830fbef75124d82786faad0e30fbe98f9ceaf11`. Opt-in squash
auto-merge then integrated the candidate as
`26e8d9ae4531645f86b7723ca4bc7a94a84aa3ee` without admin bypass, force push,
check dismissal, or conversation dismissal.

## Contained lint-scope incident

The first exploratory Ruff baseline command was broader than the protected-safe
allowlist and statically crossed sealed historical Bernie module paths. Its
output exposed only lint coordinates and import/source-structure names; it did
not open or report fixture cases, labels, expected decisions, scores, hashes,
patient/practice data, or provider output, and it executed no module or test.
Those findings were discarded and were not used for any edit. The committed
Ruff command is now an explicit allowlist, with a test prohibiting a broad
`app/services/bernie` path or any holdout-named path.

No failed acceptance gate is overridden by this containment.
