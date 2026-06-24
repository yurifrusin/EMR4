# antigravity-node-security-baseline

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 72396f8 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-node-security-baseline --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-node-security-baseline --commit-message "Node Office Security Baseline" --message "antigravity-node-security-baseline ready for Codex review"` |

## Mission

Plan and implement the Node/Office-addin supply-chain security baseline for EMR4 without changing app behavior.

## Scope

### In Scope

Plan-gated. Likely files: .github/workflows/node-security.yml or equivalent, EMR4 Sidebar/package-lock.json or package metadata only if needed for npm audit reproducibility, and concise docs/notes for local npm audit/validate commands. Focus on Office add-in dependency audit and manifest validation where practical. Also research Antigravity/Gemini's currently available plugins/skills/tools for security and developer feedback loops, and include any concrete recommendations or "not worth it yet" findings in the plan/completion notes.

### Out of Scope

Do not edit diary UI, taskpane runtime JS/CSS/HTML, backend code, migrations, Python tests, patient files, or Pages assets. Do not own Python pip-audit/Bandit; Claude owns that lane. Do not move master or handoff/current.

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

Before submit, run npm audit and any Office add-in validate/lint command that is feasible in EMR4 Sidebar, plus explain any network/tooling failures. Run git diff --check. Report exact commands and results.

## Merge Criteria

Node/Office security checks are repeatable locally or in CI, scoped to tooling/metadata, and do not alter runtime frontend behavior.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
