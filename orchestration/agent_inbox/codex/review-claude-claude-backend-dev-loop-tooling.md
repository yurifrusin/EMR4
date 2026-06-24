# review-claude-claude-backend-dev-loop-tooling

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-backend-dev-loop-tooling` |
| Status | queued |

## Review Request

claude-backend-dev-loop-tooling ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `pyproject.toml` — added `[tool.pytest.ini_options]` section with `addopts = "-q --tb=short -p no:randomly"` and `testpaths = ["tests"]`. This encodes the standard flags so agents/CI can run `python -m pytest` without repeating them.
  - `scripts/check_backend.ps1` — new Tier-1 fast check script (~15 s, no DB). Runs three sequential checks: (1) `python -m compileall app/ scripts/ -q`, (2) `bandit -r app/ -ll -ii -c pyproject.toml`, (3) `git diff --check`. Auto-detects Python path (worktree `.venv` → shared `..\..\EMR4\.venv` → system). Accepts `-SkipBandit` flag. Prints Tier-2 command hint on success. Documentation added via PowerShell `.SYNOPSIS`/`.DESCRIPTION` comment block.

- Verification run:
  - `python -m compileall app/ scripts/ -q` → exit 0, no errors.
  - `python -m bandit -r app/ -ll -ii -c pyproject.toml` → exit 0, "No issues identified." (1 low/medium-confidence skipped by `-ll -ii` threshold; 0 medium+/high).
  - `git diff --check` → exit 0, no trailing whitespace issues (CRLF normalization warnings are informational only).
  - `python -m pytest --co -q` → collected all 24 test files successfully, confirming pytest reads the new `pyproject.toml` config.
  - All three Tier-1 checks pass end-to-end.

- Remaining risks:
  - The `-p no:randomly` flag requires `pytest-randomly` to be installed for the flag to be recognized; if it's absent, pytest will still run but will log a warning. This is not a blocker — the flag just disables randomization when the plugin is present.
  - `scripts/check_backend.ps1` requires `bandit` to be installed separately (`pip install bandit`); it is not in `requirements.txt` (intentional — dev tool). The `-SkipBandit` flag handles the case where it is absent.
  - No product behaviour, clinical routes, migrations, or diary/taskpane UI were touched.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-backend-dev-loop-tooling.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
