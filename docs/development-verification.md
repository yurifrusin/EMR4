# EMR4 Development Verification

Date: 2026-07-19

## Install pinned tools

Developer and CI verification tools are separate from production dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` pins Ruff, Bandit, and pip-audit. Runtime packages remain
in `requirements.txt`.

## Canonical entry point

Run the ordinary protected-safe local profile with:

```powershell
.\.venv\Scripts\python.exe scripts\verify_repository.py --profile fast
```

Available profiles are:

- `fast`: Ruff, Python compilation, focused API Spine/handover/receipt tests,
  Diary JavaScript syntax, and Git whitespace;
- `ci-lint`: the same pinned Ruff command plus the established historical
  Diary leakage gate;
- `ci-bandit`: the exact reviewed Bandit baseline;
- `ci-security`: `ci-lint` and `ci-bandit` in one local invocation; and
- `migration`: a disposable empty-PostgreSQL upgrade/check/downgrade/re-upgrade
  lifecycle.

`scripts/check_backend.ps1` is retained as a compatibility wrapper and now
delegates to this entry point.

## Timeout and failure semantics

Verification timeouts are centralized in `scripts/verification_runtime.py`:

- ordinary tools: 120 seconds;
- focused test populations: 300 seconds;
- full or outer migration lifecycles: 900 seconds; and
- each Alembic lifecycle step: 300 seconds.

A child-process failure preserves the child's exit code. A launcher timeout is
reported separately as `launcher_timeout` and exits `124`; it is never reported
as a pytest or product failure.

## Scope and database safety

The initial Ruff gate is deliberately small: fatal syntax/runtime rules and
unused imports over an explicit ordinary product/infrastructure allowlist. It
does not enumerate sealed holdout or historical Bernie evaluation modules.
Rule or path expansion requires reviewed maintenance rather than changing
implicitly when Ruff is upgraded.

The migration profile creates only a generated database name matching
`emr4_migration_verify_<16 hex>`, validates that exact name before create/drop,
uses the configured PostgreSQL server without printing credentials, and removes
the database in a `finally` path. It never downgrades the configured development
database.

## Deferred Office bootstrap maintenance

The accepted live-local meta-grid tranche introduced
`docs/diary/office-bootstrap.js`. Off loopback it uses `document.write` with a
fixed, source-controlled Office.js URL to preserve parser-time loading before
the deferred Diary scripts. GitHub CodeQL raised an informational eval-like-call
review note; the reviewed call has no user-controlled input, the substantive
CodeQL gate passes, and the thread was resolved without suppressing a security
finding.

Leave the current loader unchanged until a bounded Office-bootstrap maintenance
tranche. That tranche should replace the call with a deterministic readiness
promise and ordered script loading, then verify normal Office-hosted loading,
loopback standalone mode, network/load failure, the full Diary smoke population,
and responsive/keyboard paths. Prefer completing it before deployment/release
hardening or the next material Office bootstrap change. This maintenance note
grants no deployment or release authority.
