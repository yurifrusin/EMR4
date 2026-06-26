# review-codex-codex-bernie-staff-pilot-gate-foundation

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-staff-pilot-gate-foundation` |
| Source Task | `codex-bernie-staff-pilot-gate-foundation` |
| Status | queued |

## Review Request

Sprint 59 dispatched: Bernie staff pilot gate foundation

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-bernie-staff-pilot-gate-foundation.md`; `orchestration/agent_inbox/codex/plan-codex-codex-bernie-staff-pilot-gate-foundation.md`
- Verification run: Plan-gate only. Ran `python scripts\agent_worktrees.py handin --agent codex`, read `AGENTS.md` and `orchestration/parallel_workstreams.md`, inspected Bernie backend/config/test surfaces, and captured the implementation plan with `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-staff-pilot-gate-foundation ...`. No production code or tests changed/run yet.
- Remaining risks: Awaiting Ariadne/Codex plan review and explicit `complete sprint task` before implementation. Main design ambiguity is standalone eligibility endpoint versus additive field on existing Bernie payloads; the submitted plan recommends a standalone non-mutating endpoint to avoid invoking proposal routes just to decide UI eligibility.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-staff-pilot-gate-foundation.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
