# review-codex-codex-sprint-g1-update-confirm-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-g1-update-confirm-invariants` |
| Status | integrated |

## Review Request

codex-sprint-g1-update-confirm-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/codex/codex-sprint-g1-update-confirm-invariants.md`
  - `orchestration/agent_inbox/codex/plan-codex-codex-sprint-g1-update-confirm-invariants.md`
- Verification run:
  - Planning mode only; read `AGENTS.md`, `orchestration/parallel_workstreams.md`, `orchestration/sprint_closeout.md`, and the task packet.
  - Ran required `handin --agent codex` with explicit venv Python path from `C:\Users\sarashera\EMR4-worktrees\codex`; succeeded and fast-forward state was already current at `5eb771b`.
  - Ran required `plan --agent codex --task codex-sprint-g1-update-confirm-invariants ...`; succeeded and wrote the implementation-plan packet.
  - No production code or tests were edited or run.
- Remaining risks:
  - Implementation decision still needed: add a native update-confirm endpoint/evidence envelope, or keep raw PUT as a bounded staff-only compatibility write while proving Bernie/model text cannot use it as confirmation authority.
  - Later implementation must run the focused backend/UI checks named in the plan before merge.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint-g1-update-confirm-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated into Sprint G1. Ariadne implemented the native update-confirm endpoint, update-purpose signed evidence, stale/current-state binding, Diary Confirm change POST path, and adversarial backend/UI checks.
- Follow-up required: Migrate human drag/drop/resize update UX to the same confirm route in G2 while preserving the current fast edit feel.
