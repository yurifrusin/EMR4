# plan-claude-claude-python-security-baseline

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-python-security-baseline` |
| Status | integrated |
| Created | 2026-06-24 10:26 +1000 |
| Source HEAD | `e1f372c` |

## Plan Summary

GitHub Actions workflow: pip-audit (CVE scan) + Bandit (static analysis); pyproject.toml bandit config; local dev commands documented

## My Understanding

Sprint 20 security baseline. Add two always-on Python security checks that run locally and in CI without secrets: (1) pip-audit for CVE scanning against requirements.txt, (2) Bandit for static security analysis of app/ code. Neither tool is installed yet. One existing workflow (pages.yml, deploy-only). No pyproject.toml. The task also asks me to research Claude Code skills/plugins for security and developer feedback loops and include findings in plan/completion notes.

## Intended Surface / Boundary

CI/build infrastructure only: .github/workflows/python-security.yml (new), pyproject.toml (new, bandit config only). No production app code changes, no migrations, no diary UI, no taskpane, no Command Centre.

## Out Of Scope

Production app behavior, migrations, diary UI, taskpane, Command Centre, seed data, patient files, authentication semantics, runtime dependencies, Node/npm audit (Antigravity lane), master/handoff/current advancement.

## Files I Expect To Edit

.github/workflows/python-security.yml -- new CI workflow: pip-audit + bandit, triggers on push/PR to any branch | pyproject.toml -- new, [tool.bandit] config section only (skip list, exclude paths)

## Implementation Steps

1. Create .github/workflows/python-security.yml: triggers on push and pull_request (all branches); single job on ubuntu-latest, Python 3.11; steps: checkout, setup-python, pip install pip-audit bandit, pip-audit -r requirements.txt --desc (fail on CVE), bandit -r app/ scripts/ -ll -ii (fail on medium+severity+confidence findings). 2. Create pyproject.toml with [tool.bandit] section: exclude_dirs=['.venv','tests','alembic'], skips=[] initially, tuned after local run. 3. Install pip-audit and bandit locally in .venv, run both commands against the repo, review findings, tune skips list if genuinely low-value noise, document all findings in completion notes. 4. Do not silently suppress real findings - if bandit flags text() SQL, JWT config, or hardcoded strings, record them for Codex to triage.

## Visual / Behavioural Acceptance Checks

python-security.yml is valid YAML. pip-audit -r requirements.txt runs to completion and either passes clean or reports CVEs with actionable names. bandit -r app/ scripts/ -ll -ii either passes or reports medium+ findings Codex can triage. No production files changed. No new runtime deps in requirements.txt.

## Risks / Ambiguities

1. pip-audit may find CVEs in python-jose (JWT confusion attacks) or cryptography - CI will fail; Codex decides whether to update dep or add scoped ignore with justification. 2. bandit may flag text() SQL calls (B608) or JWT config - document, do not suppress blindly. 3. Workflow cannot be locally run end-to-end without pushing to GitHub - will validate YAML manually and run commands locally. 4. Claude Code /security-review skill is available: runs multi-agent cloud review of branch diff. Recommendation: Codex/user should trigger it after any auth/RBAC/clinical-data route change. Not worth automating as pre-commit; CI workflow is the always-on gate.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
