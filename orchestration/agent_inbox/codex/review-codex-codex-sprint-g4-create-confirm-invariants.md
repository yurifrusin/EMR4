# review-codex-codex-sprint-g4-create-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g4-create-confirm-invariants` |
| Status | integrated |

## Review Request

codex-sprint-g4-create-confirm-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/agent_inbox/codex/codex-sprint-g4-create-confirm-invariants.md`; `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g4-create-confirm-invariants.md`.
- Verification run: Read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and this task packet; inspected the existing create proposal/confirm route, schema, diary create Save branch, and adjacent tests with `rg`/targeted file reads; plan packet captured with the explicit venv Python path. `git diff --check` to be run before submit.
- Remaining risks: Implementation must choose whether to reuse the Bernie-named create-confirm route or add a neutral staff-create-confirm alias/input without duplicating validation; direct POST compatibility must be tightly bounded so the signed-capable create UI cannot silently bypass confirm evidence; status-after-create must remain a separate PATCH that only runs after confirmed create success.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-g4-create-confirm-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted as planning/invariant guidance and integrated into Ariadne's implementation.
- Follow-up required: Continue migrating cancel/delete and status-specific write surfaces in later narrow sprints.
