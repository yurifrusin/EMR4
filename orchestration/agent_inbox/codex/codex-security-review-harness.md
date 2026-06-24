# codex-security-review-harness

| Item | Value |
|---|---|
| To | codex |
| Role | codex-worker |
| Worker Name | security-review-harness |
| Worker Branch | `codex/security-review-harness` |
| Branch | `codex/security-review-harness` |
| Status | integrated |
| Created | 72396f8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-security-review-harness --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-security-review-harness --commit-message "Security Review Harness" --message "codex-security-review-harness ready for Codex review"` |

## Mission

As a Codex worker/subagent, plan and implement the Sprint 20 security review harness: CodeQL/Dependabot coordination, a concise security checklist, and the post-integration verification path for Ariadne.

## Scope

### In Scope

Plan-gated. Role is codex-worker, branch should be codex/security-review-harness. Likely files: .github/workflows/codeql.yml, .github/dependabot.yml, orchestration/security_baseline_review.md, and small orchestration docs if needed. Include a final checklist for Ariadne using Codex Security plus local tool outputs. Also inventory Codex-side security/developer skills and plugins that should become routine for EMR4, while clearly separating installed/current tools from speculative future additions.

### Out of Scope

Do not change app/backend/frontend production behavior, tests, migrations, diary/taskpane assets, or secrets. Do not duplicate Claude's Python security workflow or Antigravity's Node audit workflow except to coordinate names/triggers. Do not use master; do not move handoff/current.

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

Run git diff --check. Validate YAML shape if workflows are changed. If feasible, run a Codex Security diff scan or document exactly how Ariadne should run it after integration.

## Merge Criteria

Ariadne has a clear review harness, CodeQL/Dependabot are configured without secrets, Codex role separation is explicit, and no production behavior changes are introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `.github/workflows/codeql.yml`, `.github/dependabot.yml`, `orchestration/security_baseline_review.md`, `orchestration/agent_inbox/codex/codex-security-review-harness.md`.
- Verification run: `git diff --check` passed; PowerShell/Python YAML parse validation passed for `.github/workflows/codeql.yml` and `.github/dependabot.yml`; Codex Security scan path and worker fallback documented in `orchestration/security_baseline_review.md`.
- Remaining risks: CodeQL build/language behaviour may need tuning after the first GitHub Actions run; Dependabot labels may need repository label creation or GitHub will create PRs without labels; Ariadne still needs to run the Codex Security diff scan after collecting all Sprint 20 submissions.
