# Ariadne Orchestrator Receipts

Date: 2026-07-11

The orchestrator receipt is a general harness control, not an EMR4 runtime
feature. It is built from three project-provided inputs:

1. `orchestrator_requirements.yaml`: continuation events, slot policy,
   workspace-receipt policy, and non-negotiable orchestration rules.
2. `transport_adapters.yaml`: how each project resource is actually reached
   and which probe methods are valid for it.
3. A transient, operator-supplied runtime-state JSON: adapter observations,
   active/stale resource-instance slots, and target-worktree receipts.

The core models only know about managed resources, active instance IDs, stale
instance IDs, and capacity. A project profile chooses which resource IDs are
managed. EMR4 currently lists `deepseek-flash-workers` because it uses a
bounded DeepSeek pool; another harness installation may list local models,
hosted agents, CI executors, human review queues, or no managed worker pool.

```powershell
.\.venv\Scripts\python.exe scripts\ariadne_orchestrator_preflight.py `
  --runtime-state tests\fixtures\ariadne_harness\orchestrator_runtime_state.json
```

The command emits `passed` or `revision_required`; it never probes providers,
spawns or closes workers, realigns worktrees, writes to a repository unless
`--output` is explicitly requested, integrates, commits, or pushes.

Every new session, post-compaction continuation, pre-sprint plan, and
pre-dispatch action requires a fresh receipt. Missing resource-instance
inventory, stale instances without recorded reuse/closure, invalid adapter
evidence, or stale worker worktrees block dispatch. This moves critical facts from a long handover
document into a repeatable, project-portable gate.

For EMR4, a post-compaction receipt is not satisfied by the boolean
`rehydrated_from_receipt` alone. The orchestrator context must record all five
named live sources in `rehydration_sources`:

- `live_handover_current_baton` — reread the current `AGENTS.md` baton rather
  than relying on a compacted conversation summary;
- `current_authority_allocation` — reread the authoritative Sol/worker/model
  allocation override;
- `active_plan_and_acceptance` — reread the current sprint contract, plan, and
  latest durable worker/review decisions;
- `protected_evidence_boundaries` — restore holdout, sensitive-data, provider,
  and write-authority constraints; and
- `git_refs_and_worktree` — verify branch, HEAD, cleanliness, protected refs,
  and the target worktree.

Missing any named source returns `revision_required` and forbids planning or
worker dispatch. Compacted summaries are continuity aids only; they are not
authoritative for agent allocation, provider transport, protected evidence, or
user decision boundaries.

## Context Health

The same receipt carries context health. Platform lifecycle events such as a
new session, compaction, restored conversation, or model/provider switch are
hard rehydration triggers. A provider may optionally report input-token and
context-limit counts; those measurements are advisory because hidden platform
context and compaction make them incomplete. The project policy uses 70% as a
checkpoint and 85% as a mandatory new-continuation threshold.

When no provider meter exists, the state is `unknown`, not healthy. Before a
high-authority action such as planning, worker dispatch, verifier acceptance,
integration, commit, or push, an unknown context must show
`rehydrated_from_receipt: true`. Worker profiles can use the same rule with a
self-contained packet receipt rather than the orchestrator's full project
receipt.
