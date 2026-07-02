# review-codex-codex-sprint104-bernie-state-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint104-bernie-state-invariants` |
| Source Task | `codex-sprint104-bernie-state-invariants` |
| Status | queued |

## Review Request

codex-sprint104-bernie-state-invariants ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- `orchestration/agent_inbox/codex/codex-sprint104-bernie-state-invariants.md` status/completion notes only.
- `orchestration/agent_inbox/codex/plan-codex-codex-sprint104-bernie-state-invariants.md` implementation plan packet.
- Verification run: `agent_worktrees.py handin --agent codex` with venv Python; `agent_worktrees.py plan --agent codex --task codex-sprint104-bernie-state-invariants ...`; read `AGENTS.md`, `implementation_plan.md`, `orchestration/parallel_workstreams.md`, `orchestration/event_driven_statechart_architecture.md`, `orchestration/bernie_interaction_model.md`, `orchestration/bernie_release_gates.md`, current Bernie transition/tests/UI surfaces, and inspected `git diff`/`git status`. No production tests run because this is a plan-only packet.
- Remaining risks: Implementation must avoid dual truth between `BernieSession` and legacy globals; `patient_booking_context` needs compact deterministic bounds; stale confirmation likely needs backend-owned ids/hashes, not only UI flags; no-slot suggestions must be typed transitions, not prompt-string shortcuts; keep limited Bernie auto-mode deferred.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint104-bernie-state-invariants.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
