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
