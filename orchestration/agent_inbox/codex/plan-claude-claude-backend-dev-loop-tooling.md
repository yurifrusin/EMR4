# plan-claude-claude-backend-dev-loop-tooling

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-backend-dev-loop-tooling` |
| Status | integrated |
| Created | 2026-06-24 17:16 +1000 |
| Source HEAD | `3780969` |

## Plan Summary

Two deliverables: (1) add [tool.pytest.ini_options] to pyproject.toml so 'python -m pytest' encodes all standard flags; (2) new scripts/check_backend.ps1 Tier-1 fast check (compileall app/ scripts/, bandit -r app/, git diff --check, ~15s, no DB). Together they give Ariadne a documented two-tier sequence: Tier-1 fast before every submit, Tier-2 full pytest for regression. No new pip deps, no product/test/migration changes.

## My Understanding

Ariadne currently hand-types per-file py_compile, per-file bandit, and targeted pytest flags every sprint. There is no single run-before-submit command. The full suite takes ~7 min and has no defined fast subset. This leads to inconsistent checks and easy-to-miss steps. The fix is pytest config in pyproject.toml plus a fast Tier-1 script.

## Intended Surface / Boundary

pyproject.toml (edit: add [tool.pytest.ini_options]) + scripts/check_backend.ps1 (new file). No changes to app/, tests/, alembic/, docs/, taskpane, diary, run_dev.ps1, or AGENTS.md.

## Out Of Scope

Product/clinical code, test changes, migrations, new pip deps (ruff/mypy/flake8), run_dev.ps1 changes, AGENTS.md edits, WhatsApp/notification scripts, database schema.

## Files I Expect To Edit

pyproject.toml, scripts/check_backend.ps1

## Implementation Steps

1. Edit pyproject.toml: add [tool.pytest.ini_options] with addopts='-q --tb=short -p no:randomly' and testpaths=['tests']. 2. Create scripts/check_backend.ps1: header comment naming bandit install requirement; Step 1 python -m compileall app/ scripts/ -q; Step 2 python -m bandit -r app/ -ll -ii -c pyproject.toml; Step 3 git diff --check; exit 0 with Tier-2 hint on success, exit 1 on first failure. 3. Verify: python -m pytest --co -q (collect-only, confirms pyproject.toml config works); run scripts/check_backend.ps1 on clean tree; git diff --check.

## Visual / Behavioural Acceptance Checks

python -m pytest (no args) runs full suite with -q --tb=short -p no:randomly; scripts/check_backend.ps1 exits 0 on clean tree in <30s without DB; scripts/check_backend.ps1 exits 1 if compileall finds a syntax error; existing 254 tests continue to pass.

## Risks / Ambiguities

1. -p no:randomly warns but does not fail if pytest-randomly not installed. 2. bandit not in requirements.txt (dev tool); script header documents the install requirement. 3. compileall on scripts/ compiles large agent_worktrees.py — safe, tested clean. 4. pyproject.toml addopts will affect all pytest invocations including CI if CI uses this file — verify CI does not use a separate pytest.ini that would conflict (none found).

## Codex Plan Review

- Review result: Accepted during Sprint 22 plan review.
- Required changes before implementation: None.
- Approved to proceed: yes; implementation was released with `complete sprint task`.
