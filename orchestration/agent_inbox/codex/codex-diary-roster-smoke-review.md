# codex-diary-roster-smoke-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/diary-roster-smoke-review` |
| Status | integrated |
| Created | 2f511a1 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-diary-roster-smoke-review --commit-message "Add diary roster smoke review" --message "Diary roster smoke review ready for Codex review"` |

## Mission

Prepare the review and smoke-test surface for the roster-consumption sprint without implementing backend or frontend roster logic owned by Claude and Antigravity.

## Scope

### In Scope

- Inspect existing diary smoke mode, sprint closeout, and orchestration review expectations.\n- Add or update lightweight documentation/checklist artifacts under orchestration/ if useful for reviewing roster consumption after worker submits.\n- If safe and non-overlapping, add a tiny smoke-mode-only fixture or note that helps verify roster fallback/label behaviour, but do not compete with Antigravity's production frontend implementation.\n- Identify exact manual browser checks Codex should run after integrating Claude and Antigravity.\n- Keep changes small and review-oriented.

### Out of Scope

- Do not edit backend app/models, app/schemas, app/routers, migrations, seed, or tests; Claude owns that.\n- Do not implement production docs/diary roster fetching/merging; Antigravity owns that.\n- Do not edit taskpane, command-centre, consultation AI, Gemini, or booking mutation logic.\n- Do not push to master or handoff/current manually.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Create or switch to the worker branch from the current handoff tip before editing:
   `git switch -C codex/diary-roster-smoke-review handoff/current`.
5. Work only inside the stated scope unless the user or Codex expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Finish with the submit command above.

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

- If any JS is touched, run node --check docs\\diary\\diary.js.\n- Run git diff --check.\n- Provide a concise post-integration review checklist in Completion Notes.

## Merge Criteria

- Provides Codex with a clearer review/test path for roster consumption.\n- Does not duplicate or conflict with Claude/Antigravity implementation scopes.\n- Keeps sprint implementation gate intact and avoids booking mutation work.

## Dissent / Risks

- This task deliberately avoids JS/backend changes, so it cannot prove roster
  rendering by itself. The checklist should be applied only after the Claude and
  Antigravity submits are integrated locally.
- The most important residual risk is ambiguous fallback semantics: an empty
  roster should fall back to template columns, while auth failure should remain a
  real session-expired state rather than silently hiding a permissions issue.

## Completion Notes

Fill this in before submit:

- Files changed: `orchestration/diary_roster_smoke_review.md`;
  `orchestration/agent_inbox/codex/codex-diary-roster-smoke-review.md`.
- Verification run: `git diff --check` passed. No JS touched, so
  `node --check docs\diary\diary.js` is not required.
- Remaining risks: Browser checks are review instructions only; the actual
  roster fetch/merge behaviour depends on the separately owned Claude and
  Antigravity workstreams.
