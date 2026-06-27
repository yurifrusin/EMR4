# review-codex-codex-bernie-interpret-booking-instruction

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-interpret-booking-instruction` |
| Source Task | `codex-bernie-interpret-booking-instruction` |
| Status | queued |

## Review Request

Sprint 63 dispatched: Bernie interpret booking instruction endpoint

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Files changed: `orchestration/agent_inbox/codex/codex-bernie-interpret-booking-instruction.md`; `orchestration/agent_inbox/codex/plan-codex-codex-bernie-interpret-booking-instruction.md`
- Verification run: Plan gate only; no production code, tests, docs, migrations, or runtime files edited. Ran `python scripts\agent_worktrees.py handin --agent codex` and `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-interpret-booking-instruction ...`.
- Remaining risks: Implementation not started; Ariadne still needs to approve endpoint placement, response naming, and disabled-default response semantics before sending `complete sprint task`.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-interpret-booking-instruction.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
