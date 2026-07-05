# Blocker Note

Python is not available in this sandbox — python, python3, py not found in PATH.
Cannot run:
  python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r6-temporal-edge-scout --commit-message "Plan R6 temporal edge scout" --message "Plan packet submitted; no production code changes."

## Workaround

The plan artifact lives at two locations:
- docs/receptionist_review_r6_edge_cases.md (canonical doc)
- orchestration/agent_inbox/codex/codex-sprint-r6-temporal-edge-scout.plan.md

The submit path requires Ariadne to run from the integration worktree where Python is available, or to copy the plan artifact manually and commit it.

## Git Status

- Branch: codex/sprint-r6-temporal-edge-scout
- Uncommitted: docs/receptionist_review_r6_edge_cases.md and orchestration/agent_inbox/codex/codex-sprint-r6-temporal-edge-scout.plan.md
