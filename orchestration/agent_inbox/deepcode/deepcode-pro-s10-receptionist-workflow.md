# DeepSeek Pro Conductor - S10 End-to-End Receptionist Workflow

Date: 2026-07-13
Role: routine Conductor
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro` / high
Expected artifact:
`orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`

## Authority and Current Gate

You are the sole S10 sprint-definition and worker-allocation authority. GPT
Terra is the bounded executor only: it may review executability, issue one
rejoinder only for a material executability or pilot-boundary failure, dispatch
your allocated workers, request same-lane corrections, run deterministic gates,
and integrate accepted commits only onto its staging branch.

The prior S10 preflight escalation is preserved at
`orchestration/agent_inbox/codex/s10-terra-preflight-escalation.md`. Sol
resolved its generic policy cause on protected master at `b05ee20a`; the fresh
Terra pre-sprint planning receipt now passes with `assigned_agent_ids: []`.
Do not treat historical unassigned Claude or Antigravity mirrors as blockers.

## Programme Direction

Define and allocate S10 only: the approved S9-S12 operational-hardening
tranche's end-to-end receptionist workflow sprint. Inspect the current code,
the S8 receptionist workflow closeout, S9 local Diary development-loop plan and
review, current harness settings, and the existing Bernie/Diary route and
workflow evidence before deciding the bounded implementation surface.

The plan must produce concrete, provider-free, receptionist-facing workflow
progress with executable deterministic evidence. Do not allocate S11 or S12,
and do not reopen closed runtime or product-policy gates merely to make S10
larger.

Terminal-to-active appointment status policy remains user-owned and must not be
chosen, inferred, or implemented. Provider/live-provider, database/schema,
external patient client, H15/H-series, historical diary trove, memory/RAG/
GraphRAG, new model-write gates, deployment, release, and protected-master
authority remain closed.

## Required Plan

Inspect before deciding. Publish an executable Conductor plan containing every
field required by `orchestration/harness_settings/sprint_worker_policy.yaml`:

- boundary, direction disposition, and current settings fingerprint;
- exact evidence, bounded scope, and closed-gate exclusions;
- non-overlapping worker assignments, models, reasoning, packets, and
  ownership boundaries;
- explicit assigned-agent workspace receipts needed before each worker dispatch;
- injected shared Python and Node paths;
- deterministic worker and independent Terra acceptance evidence;
- review posture, retry/recovery posture, commit checkpoints, and fallback
  reasons;
- independence labels, unfilled obligations, and no monetary or wall-clock cap;
- an explicit statement that the Conductor does not dispatch, accept, integrate,
  commit, push, alter protected master, or advance `handoff/current`.

The final plan and allocations are yours. Do not edit product code or tests in
this turn. Write only the expected durable plan artifact and end it with
`STATUS: complete`.
