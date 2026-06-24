# review-claude-claude-python-security-baseline

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-python-security-baseline` |
| Status | integrated |

## Review Request

claude-python-security-baseline ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `.github/workflows/python-security.yml` (new) — triggers on push + pull_request; installs pip-audit and bandit as CI-only tools; runs `pip-audit -r requirements.txt --desc` (fails on CVE) then `bandit -r app/ scripts/ -ll -ii` (fails on medium+ severity + confidence). YAML comments document the two known CVEs and how to clear them once deps are bumped.
  - `pyproject.toml` (new) — `[tool.bandit]` section only: `exclude_dirs = [".venv", "tests", "alembic"]`, `skips = []` (nothing suppressed).

- Verification run:
  - `bandit -r app/ scripts/ -ll -ii -c pyproject.toml` → **No issues identified** (5590 lines scanned; 4 low-severity findings all correctly filtered by `-ll -ii`).
  - `pip-audit -r requirements.txt --desc` → **exit 1 — 2 CVEs found** (documented below). The workflow will fail until `requirements.txt` is bumped.
  - Bandit full run (all severities) — 4 low-severity findings, all expected and appropriately filtered:
    - B105 `app/config.py:5` — `'change-me-in-production'` default key (intentional placeholder; fail-closed logic already guards this in config.py)
    - B110 `app/routers/consultation.py:103` — `try/except/pass` (swallows Vertex AI exception silently; low risk, worth a future review)
    - B404/B603 `scripts/agent_worktrees.py` — subprocess import/call (expected in the orchestration helper; shell=False is the safer path)

- pip-audit CVE findings — **REAL, require dep bumps in requirements.txt**:
  1. `cryptography 48.0.0` — **GHSA-537c-gmf6-5ccf** — OpenSSL vulnerability in PyPI-distributed wheels (statically linked). Fix: `cryptography==48.0.1`. **Recommended action: bump immediately** — cryptography is used for JWT handling and TLS; the bundled OpenSSL has a known security advisory.
  2. `pydantic-settings 2.14.1` — **GHSA-4xgf-cpjx-pc3j** — symlink traversal in `NestedSecretsSettingsSource` with `secrets_nested_subdir=True`. Fix: `pydantic-settings==2.14.2`. **Lower urgency for EMR4** — EMR4 uses env-var/dotenv config, not `NestedSecretsSettingsSource`; however the fix is trivial and should be taken.

- Claude Code security skills research findings:
  - `/security-review` skill is available: runs a multi-agent cloud review of the current branch diff. **Recommendation:** trigger after any auth, RBAC, or clinical-data route change. Not worth automating as a pre-commit hook — the GitHub Actions workflow is the always-on gate; `/security-review` is the on-demand deep-dive complement.
  - `/code-review` skill also available for broader correctness + efficiency review.

- Remaining risks:
  - The CI workflow will fail on both CVE findings until `requirements.txt` bumps `cryptography` to 48.0.1 and `pydantic-settings` to 2.14.2. Codex should do a follow-up dep-bump task or incorporate into current integration. Neither bump is a behavior change.
  - `B110 try/except/pass` in `consultation.py:103` is a genuine low-severity finding suppressed by `-ll`. Worth a future fix (log the exception rather than silently swallowing it).
  - The workflow does not cover Node/Office npm audit (Antigravity lane) or secrets rotation.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-python-security-baseline.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
