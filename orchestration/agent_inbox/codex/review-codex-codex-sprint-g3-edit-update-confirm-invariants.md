# review-codex-codex-sprint-g3-edit-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g3-edit-update-confirm-invariants` |
| Status | integrated |

## Review Request

codex-sprint-g3-edit-update-confirm-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/codex-sprint-g3-edit-update-confirm-invariants.md`
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g3-edit-update-confirm-invariants.md`
- Verification run:
  - Planning mode only; read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and `orchestration/agent_inbox/codex/codex-sprint-g3-edit-update-confirm-invariants.md`.
  - Ran required `handin --agent codex` with explicit venv Python path from `C:\Users\sarashera\EMR4-worktrees\codex`; succeeded and reported already up to date at `84a0934`.
  - Ran required `plan --agent codex --task codex-sprint-g3-edit-update-confirm-invariants ...`; succeeded and wrote the implementation-plan packet.
  - Focus-read the edit modal `saveBooking()` raw-PUT/status-PATCH branch, the G2 drag/resize signed confirm pattern, update-confirm backend contract, and existing update-confirm tests.
  - No production code or tests were edited or run.
- Remaining risks:
  - Later implementation must prevent a stale/tampered failed detail update confirm from still sending the separate status PATCH.
  - If an old-backend raw PUT fallback is retained, it must be explicit and must not run when signed confirm evidence is available.
  - The update-confirm schema remains Bernie-named; avoid unnecessary renaming unless Ariadne accepts the compatibility work.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-g3-edit-update-confirm-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted. Ariadne implemented the invariant plan directly on master after plan review.
- Follow-up required: Later sprints should continue migrating other write surfaces to typed signed confirms before retiring raw compatibility endpoints.
