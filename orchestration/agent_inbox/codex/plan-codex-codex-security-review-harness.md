# plan-codex-codex-security-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/security-review-harness` |
| Source Task | `codex-security-review-harness` |
| Status | integrated |
| Created | 2026-06-24 10:10 +1000 |
| Source HEAD | `e1f372c` |

## Plan Summary

Plan security review harness

## My Understanding

Build a Sprint 20 security review harness after approval: repository automation for CodeQL/Dependabot coordination, a concise Ariadne-facing security baseline checklist, and a repeatable post-integration verification path combining Codex Security and local tool outputs. This is a harness/review surface only, not a production behavior change.

## Intended Surface / Boundary

Security/orchestration infrastructure only: GitHub workflow/dependency configuration and orchestration review documentation. No visual UI surface is affected. Nearby visually loaded diary/taskpane concepts — cards, slots, stacking, panels, waiting room, diary grid, booking slot, and status — must not change.

## Out Of Scope

No edits to app/, backend/frontend behavior, migrations, seed data, pytest suites, diary/taskpane/Command Centre assets, secrets, or deployment behavior beyond safe GitHub security configuration. Do not duplicate Claude's Python security workflow or Antigravity's Node audit workflow except by naming how Ariadne should coordinate their outputs.

## Files I Expect To Edit

.github/workflows/codeql.yml; .github/dependabot.yml; orchestration/security_baseline_review.md; possibly a small cross-reference in an orchestration coordination file only if needed for discoverability.

## Implementation Steps

Inspect existing GitHub workflows and dependency manifests; add minimal CodeQL config for Python/JavaScript without secrets; add Dependabot schedules for GitHub Actions, pip, and npm ecosystems discovered in repo; draft the Ariadne checklist with local checks, Codex Security diff/scan guidance, and worker-output coordination; inventory current installed Codex security/developer skills/plugins separately from speculative future additions; keep all changes narrow and documentation/config-only.

## Visual / Behavioural Acceptance Checks

No app, diary, taskpane, waiting-room, booking, or status UI behavior changes. GitHub config parses as YAML. Checklist gives Ariadne concrete commands/outputs to collect and explicitly preserves codex-worker vs Ariadne role separation.

## Risks / Ambiguities

CodeQL language/build mode may need tuning after first GitHub Actions run; Dependabot ecosystem paths depend on exact manifest layout; Codex Security may require Ariadne's app-mediated scan flow after integration, so the harness should document the exact fallback when a worker cannot run it directly.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
