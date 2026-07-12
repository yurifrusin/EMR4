# DeepSeek Pro Conductor - S9 Local Diary Development Loop

Date: 2026-07-13
Role: routine Conductor
Resource: `deepseek-pro-conductor-fallback` (routine-first policy)
Model: `deepseek-v4-pro` / high
Expected artifact:
`orchestration/agent_inbox/codex/plan-deepseek-pro-s9-local-diary-dev-loop.md`

## Programme Direction

Define and allocate S9, the first sprint of the approved S9-S12 receptionist
operational-hardening tranche:

- S9: local Diary development loop;
- S10: end-to-end receptionist workflow;
- S11: appointment API operational hardening;
- S12: receptionist acceptance checkpoint.

Only S9 should be executable now. Preserve the tranche direction without
prematurely allocating S10-S12.

## S9 Advisory Scope

Verify the S8 taskpane resolver's port-3000 local Diary URL against the actual
development stack. Inspect `run_dev.ps1`, Sidebar dev-server configuration,
`sync_taskpane.py`, manifest/taskpane origins, Diary static hosting, and existing
review harnesses. If local launch does not work end to end, define the smallest
cross-platform-sympathetic repair and regression evidence.

The sprint should produce substantive EMR4 development-loop behavior, not only
an inventory. It may change bounded development scripts/configuration and tests,
but not production deployment authority or runtime clinical contracts.

Terminal-to-active appointment-status policy remains user-owned and out of
scope. Provider/live-provider, database/schema migration, external patient
client, H15/H-series, historical diary, memory/RAG/GraphRAG, Bernie D5, and new
model-write gates remain closed.

## Required Plan

Inspect current code before deciding. Publish an executable Conductor plan with:

- direction disposition and current settings fingerprint;
- exact defect/evidence and bounded implementation surface;
- worker allocation from the current pool, with non-overlapping ownership;
- use of injected shared Python/Node tools;
- focused and end-to-end acceptance evidence;
- review posture, regular commit/push checkpoints, and closed gates;
- explicit statement that no monetary or wall-clock caps are active.

DeepSeek Pro has final sprint-definition/allocation authority. Sol may issue one
rejoinder only for a material executability concern. Do not edit product code or
tests in this Conductor turn. Write only the expected durable plan artifact and
end with `STATUS: complete`.
