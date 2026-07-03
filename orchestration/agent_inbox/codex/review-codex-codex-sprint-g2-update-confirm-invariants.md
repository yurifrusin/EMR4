# review-codex-codex-sprint-g2-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g2-update-confirm-invariants` |
| Status | integrated |

## Review Request

codex-sprint-g2-update-confirm-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/codex-sprint-g2-update-confirm-invariants.md`
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g2-update-confirm-invariants.md`
- Verification run:
  - Planning mode only; read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and `orchestration/agent_inbox/codex/codex-sprint-g2-update-confirm-invariants.md`.
  - Ran required `handin --agent codex` with explicit venv Python path from `C:\Users\sarashera\EMR4-worktrees\codex`; succeeded and reported already up to date at `85166f0`.
  - Ran required `plan --agent codex --task codex-sprint-g2-update-confirm-invariants ...`; succeeded and wrote the implementation-plan packet.
  - Focus-read G1 update-confirm backend route/schema/tests and Diary human edit/drag/resize raw-PUT call sites.
  - No production code or tests were edited or run.
- Remaining risks:
  - Later implementation must decide whether to neutralize the Bernie-named update-confirm schema or keep a compatible alias while avoiding G1 regressions.
  - Diary edit modal currently combines appointment update with a separate status PATCH; G2 must not accidentally fold status semantics into the update-confirm route.
  - Raw PUT should remain a bounded authenticated staff/API compatibility path, but the migrated Diary confirm UI must not use it as confirmation authority.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-g2-update-confirm-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated into Sprint G2. Ariadne implemented confirm evidence on ordinary update proposals, moved human drag/drop/resize confirms to `/appointments/proposals/update/confirm`, and added backend/UI invariant coverage.
- Follow-up required: Edit-form Save still uses the bounded raw PUT compatibility path and should be migrated in a separate sprint.
