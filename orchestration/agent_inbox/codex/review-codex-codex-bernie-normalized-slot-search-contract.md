# review-codex-codex-bernie-normalized-slot-search-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-normalized-slot-search` |
| Source Task | `codex-bernie-normalized-slot-search-contract` |
| Status | queued |

## Review Request

codex-bernie-normalized-slot-search-contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/plan-codex-codex-bernie-normalized-slot-search-contract.md`; coordination status update in `orchestration/agent_inbox/codex/codex-bernie-normalized-slot-search-contract.md`.
- Verification run: Plan gate only. Ran `python scripts\agent_worktrees.py handin --agent codex`; read printed protocol alerts and task packet; read `AGENTS.md` and `orchestration/parallel_workstreams.md`; inspected existing slot-search normalizer/proposal contracts for planning context. No production code tests run because no production code was changed.
- Remaining risks: Implementation still requires Ariadne approval before coding. Proposed route/helper naming and response wrapper shape should be confirmed during review; implementation must keep unsafe normalization from executing slot search and must reuse existing non-mutating proposal logic for safe requests.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-normalized-slot-search-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
