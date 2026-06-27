# review-codex-codex-bernie-interpret-live-provider-runway

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-interpret-live-provider-runway` |
| Source Task | `codex-bernie-interpret-live-provider-runway` |
| Status | queued |

## Review Request

Sprint 64 dispatched for Codex worker plan gate

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md`; `orchestration/agent_inbox/codex/plan-codex-codex-bernie-interpret-live-provider-runway.md`
- Verification run: Plan gate only; no production code edited and no runtime tests run. Intake/read commands completed; plan captured with `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-interpret-live-provider-runway ...`; git diff hygiene checked before submit.
- Remaining risks: Implementation not started. Ariadne must review/approve the plan and send exact `complete sprint task` before any backend/config/test edits.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
