# review-codex-codex-bernie-pilot-context-selector

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-pilot-context-selector` |
| Source Task | `codex-bernie-pilot-context-selector` |
| Status | queued |

## Review Request

Sprint 62 dispatched: Bernie pilot context selector

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-bernie-pilot-context-selector.md`; this source packet status/completion notes only.
- Verification run: Plan gate only; no production code or review harness changes made. Intake command `python scripts\agent_worktrees.py handin --agent codex` succeeded from `C:\Users\YuriFrusin\Documents\EMR4` on branch `master`, then worker branch `codex/bernie-pilot-context-selector` was created. Plan command `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-pilot-context-selector --summary "Sprint 62 plan: Bernie pilot explicit context selector" ...` succeeded on `codex/bernie-pilot-context-selector`. `git diff --check` passed with the existing CRLF normalization warning for this packet.
- Remaining risks: Implementation still needs Ariadne approval with `complete sprint task`; ordinary-mode context validation must avoid smoke/default fallback without blocking future legitimate IDs, and route-intercepted tests must prove zero real writes.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-pilot-context-selector.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
