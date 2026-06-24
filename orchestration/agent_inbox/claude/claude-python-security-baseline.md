# claude-python-security-baseline

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 72396f8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-python-security-baseline --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-python-security-baseline --commit-message "Python Security Baseline" --message "claude-python-security-baseline ready for Codex review"` |

## Mission

Plan and implement a small Python/backend security baseline for EMR4: fast dependency and static-analysis checks that can run locally and in GitHub Actions without requiring secrets.

## Scope

### In Scope

Plan-gated. Likely files: .github/workflows/python-security.yml or equivalent, requirements/security tool notes if needed, minimal docs for exact commands. Consider pip-audit and Bandit for app/ while avoiding noisy/generated paths. Keep checks deterministic and Windows/GitHub Actions friendly. Also research Claude Code's currently available plugins/skills/tools for security and developer feedback loops, and include any concrete recommendations or "not worth it yet" findings in the plan/completion notes.

### Out of Scope

Do not change production app behavior, migrations, diary UI, taskpane/Command Centre, seed data, patient files, authentication semantics, or runtime dependencies unless the plan justifies a tiny dev-only tooling dependency. Do not handle Node/Office npm audit; Antigravity owns that lane. Do not move master or handoff/current.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Before submit, run the new local Python security commands if feasible, plus .venv\Scripts\python.exe -m py_compile over any changed Python helper files. If adding GitHub Actions only, validate YAML shape and document any commands that require network. Report exact command output.

## Merge Criteria

Ariadne can run or clearly understand the Python security checks; failures are actionable rather than noisy; no production behavior changes; workflow/docs are scoped and do not require secrets.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
