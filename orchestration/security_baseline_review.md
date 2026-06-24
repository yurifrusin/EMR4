# Sprint 20 Security Baseline Review Harness

This is Ariadne's post-integration security review checklist for Sprint 20. It
coordinates GitHub-native security signals, local tool output, Codex Security,
and worker submissions without changing EMR4 runtime behavior.

## Scope Boundary

- Review surface: GitHub security configuration and orchestration notes.
- Runtime surfaces intentionally unchanged: backend API, database migrations,
  tests, diary grid, taskpane, Command Centre, booking slots, waiting room,
  panels, cards, stacking, appointment status controls, and secrets.
- Role separation: codex-worker prepares the harness; Ariadne/orchestrator
  reviews, integrates, runs final scans, and decides whether to push `master`
  and `handoff/current`.

## GitHub Security Configuration

- CodeQL lives in `.github/workflows/codeql.yml`.
  - Runs for Python and JavaScript/TypeScript.
  - Uses `security-extended` and `security-and-quality` query suites.
  - Triggers on pull requests to `master`, relevant pushes to `master`, weekly
    scheduled analysis, and manual dispatch.
  - Requires no repository secrets.
- Dependabot lives in `.github/dependabot.yml`.
  - Tracks GitHub Actions at `/`.
  - Tracks Python dependencies from `/requirements.txt`.
  - Tracks Node dependencies from `/EMR4 Sidebar/package-lock.json`.
  - Uses weekly Tuesday morning Brisbane schedules with staggered times.

## Ariadne Review Checklist

Before integrating Sprint 20:

1. Confirm each worker stayed inside its approved boundary:
   - Claude: Python security workflow only.
   - Antigravity: Node audit workflow/amendment only.
   - Codex worker: CodeQL, Dependabot, and this orchestration checklist only.
2. Inspect workflow names and triggers for duplication or noisy overlap:
   - CodeQL should own GitHub code scanning.
   - Claude's workflow should own Python dependency/static checks.
   - Antigravity's workflow should own Node dependency/static checks.
3. Run local static verification from the integration worktree:
   - `git diff --check`
   - YAML parse validation for changed `.yml` / `.yaml` files.
   - Any focused workflow-lint command Ariadne has available locally.
4. Review dependency scope:
   - `requirements.txt` is covered by Dependabot `pip`.
   - `EMR4 Sidebar/package-lock.json` is covered by Dependabot `npm`.
   - `.github/workflows/*.yml` is covered by Dependabot `github-actions`.
5. Confirm no secrets, patient data, `.env` values, generated documents, or
   local runtime files appear in the diff.
6. Confirm no production runtime surfaces changed unless Ariadne explicitly
   approved a bounded hotfix during integration.

## Codex Security Path

Preferred Ariadne path after collecting all Sprint 20 submissions:

1. Open a Codex Security workspace against the integration worktree.
2. Use Review changes / diff mode for the complete Sprint 20 integration diff.
3. Focus the user context on security baseline configuration, GitHub workflow
   permissions, dependency-audit coverage, and accidental runtime-surface drift.
4. Validate any reported finding against the local diff before integrating.
5. Record confirmed or intentionally deferred findings in
   `orchestration/sprint_closeout.md`.

Worker fallback if the app-mediated Codex Security scan cannot be run from a
subagent:

- Document that Ariadne must run the scan after merging worker submissions into
  the integration worktree.
- Provide the exact local verification already run by the worker.
- Do not substitute an unreviewed manual push to `master` or `handoff/current`.

## Installed Codex-Side Security / Developer Capabilities

Current capabilities visible to this Codex session that should become routine
for EMR4 security work:

- `codex-security:security-diff-scan` for PR, commit, branch, or working-tree
  security reviews.
- `codex-security:security-scan` for repository-wide or scoped security scans.
- `codex-security:deep-security-scan` for multi-pass exhaustive repository scans.
- `codex-security:triage-finding`, `codex-security:validation`, and
  `codex-security:attack-path-analysis` for scanner output and candidate-finding
  review.
- `codex-security:fix-finding` for bounded remediation after a finding is
  validated and approved.
- `emr4-orchestrator` for Sprint protocol, role separation, worker submission,
  and integration discipline.

Speculative future additions are intentionally not listed as installed tools.
If Ariadne wants more automation later, capture it as a new task packet rather
than folding it into Sprint 20.

## Expected Closeout Evidence

For the Sprint 20 closeout, Ariadne should record:

- GitHub workflow files changed and why.
- Local validation commands and results.
- Codex Security scan mode or documented reason it could not run before push.
- Any CodeQL/Dependabot first-run caveats.
- Confirmation that diary/taskpane/backend runtime behavior was not changed by
  the security harness.
