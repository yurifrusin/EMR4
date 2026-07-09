# Ariadne Multi-Agent SSDLC Harness Blueprint

Date: 2026-07-09

Status: fragile blueprint. This is documentation only. It does not implement or
approve live subagent execution, autonomous commits, provider calls, route
wiring, database writes, deployment, production readiness, PHI access,
historical diary access, memory/RAG/GraphRAG, or any EMR4 runtime behavior.

## Purpose

This document captures the proposed sidecar harness that grew out of the Bernie
determinism work and the experience of trying to make Ariadne predictably
orchestrate multiple coding agents.

The target is broader than EMR4: a cross-platform, secure-SDLC-native
orchestration harness for software development. EMR4 is the first testbed, but
the harness should be useful to a solo developer with one agent, a project lead
with many LLM workers, or a team mixing humans, CI, local tools, and hosted
agents.

The central problem is not only how to control subagents. The harder and more
important problem is how to control the orchestrator without destroying the
reason the user relies on the orchestrator: strategic intelligence, sprint
planning, decomposition, synthesis, and momentum.

## Design Thesis

The user approves an operating envelope. The orchestrator autonomously finds the
best path inside that envelope. A deterministic harness blocks, pauses, or
escalates only when the orchestrator tries to leave the envelope or skip required
SSDLC evidence.

In short:

- autonomy inside the corridor;
- escalation at the boundary;
- deterministic authority outside the orchestrator's prose;
- stable SSDLC obligations regardless of how many agents are available.

The orchestrator should be intelligent about planning, decomposition, and
tradeoffs. It should not be trusted to interpret its own authority at the moment
authority matters.

## Non-Goals

The first version must not try to become a full multi-agent runtime.

Do not start with:

- live control of Codex, Claude, Antigravity, or other worker agents;
- automatic commits or pushes;
- deployment decisions;
- production readiness scoring;
- provider/model orchestration;
- secret, PHI, or patient-data handling;
- direct integration into EMR4 clinical runtime paths;
- broad refactor authority.

Start with contracts, validators, synthetic replay scenarios, mock worker
packets, and safe aggregate reports.

## Core Invariants

1. The SSDLC is fixed. The staffing model is elastic.

   The harness defines required development obligations by stage. Available
   resources are mapped onto those obligations dynamically.

2. Roles are contracts. Agents are resources.

   `security_reviewer`, `test_engineer`, and `docs_handover_auditor` are role
   obligations, not necessarily separate people or models.

3. The orchestrator proposes. The deterministic harness authorizes.

   The orchestrator may propose a sprint, action, delegation, or closeout. A
   validator decides whether it is allowed, approval-required, blocked, or
   underspecified.

4. The orchestrator cannot self-authorize boundary crossings.

   A natural next step is not permission. A precedent is not permission. A
   successful review is not runtime authority.

5. Evidence promotes stages.

   Work does not move from design to implementation, implementation to
   integration, or integration to release just because the orchestrator believes
   it is ready. Required artifacts must exist.

6. Reduced independence is recorded, not hidden.

   A one-agent workflow can proceed, but self-review must be labelled as such
   and may require stronger deterministic checks or human approval before
   promotion.

7. Refusal and pause are first-class outcomes.

   `request_user_boundary_approval`, `stop_at_boundary`,
   `refuse_missing_authority`, and `request_clarification` are successful
   harness outcomes, not failures of initiative.

## Cross-Platform Baseline

The deterministic core should be a Python package and CLI, portable across
Windows, Linux, and macOS.

Required implementation choices:

- use `pathlib.Path` for filesystem paths;
- store contracts and replay fixtures as JSON, JSONL, or YAML with explicit
  schemas;
- move to SQLite when real concurrency or durable event queries matter;
- represent process calls as argument arrays, not shell strings;
- avoid PowerShell/Bash semantics in core logic;
- keep OS differences inside adapters only;
- use repo-relative paths in fixtures and reports;
- make file locking, executable discovery, and terminal behavior adapter
  concerns.

The first coordination protocol should be filesystem packets:

```text
orchestration_harness/
  mandates/
  runs/
  inbox/
    worker-name/
  outbox/
    worker-name/
  events/
  reports/
```

This lets a worker be an LLM, a human, a CI job, or a mock test fixture without
changing the SSDLC contract.

## SSDLC Spine

The harness should model software work as stage transitions with evidence
requirements.

| Stage | Orchestrator autonomy | Required evidence |
|---|---|---|
| Intake | clarify objective, scope, risk, mandate | goal, boundaries, stop conditions |
| Design | propose architecture and sprint split | design note, assumptions, affected modules |
| Threat Model | identify security and abuse cases | threat model or not-applicable rationale |
| Implementation | produce bounded changes | patch, scope check, changed-file inventory |
| Verification | run tests and checks | command evidence, failures, residual gaps |
| Review | delegate or perform review roles | findings, severity, disposition |
| Integration | update docs and prepare checkpoint | diff summary, gate check, handover update |
| Release/Closeout | commit, push, notify, or stop | audit log, residual risk, approval state |

The orchestrator can autonomously move through approved stages inside the
mandate. It must pause before crossing a boundary class such as:

- test-only to runtime;
- provider-free to provider-connected;
- read-only to mutating;
- synthetic fixture to real data;
- local-only to external;
- design/review to production readiness;
- proposal to release authority.

## Mandate Ledger

The user should approve a mandate once, then the orchestrator should operate
inside it without repeatedly asking for sprint-level permission.

Example:

```json
{
  "mandate_id": "emr4-ariadne-harness-blueprint",
  "objective": "Develop a docs/tests-only sidecar orchestration harness blueprint",
  "autonomy": "continue_green_and_blue_sprints",
  "allowed": [
    "docs",
    "tests",
    "static_contracts",
    "synthetic_fixtures",
    "mock_worker_packets",
    "safe_aggregate_reports"
  ],
  "requires_user_approval": [
    "live_subagent_execution",
    "runtime_wiring",
    "provider_calls",
    "database_writes",
    "real_patient_data",
    "deployment",
    "production_readiness_claims"
  ],
  "stop_conditions": [
    "scope_boundary_crossing",
    "missing_required_evidence",
    "subagent_review_conflict",
    "dirty_worktree_conflict",
    "security_sensitive_change_without_threat_model"
  ]
}
```

The orchestrator may choose the next sprint inside this mandate. It may not
expand the mandate by interpreting chat history or project momentum.

## Orchestrator Action Grammar

The orchestrator should operate through typed actions.

Initial action vocabulary:

- `inspect_context`
- `define_next_sprint`
- `classify_boundary`
- `assign_role`
- `delegate_review`
- `delegate_implementation`
- `propose_patch`
- `apply_patch`
- `run_verification`
- `record_evidence`
- `update_handover`
- `commit_checkpoint`
- `push_checkpoint`
- `request_user_boundary_approval`
- `request_clarification`
- `stop_at_boundary`
- `refuse_missing_authority`

Every proposed action should be classifiable as one of:

- `allowed`
- `allowed_with_evidence`
- `requires_user_approval`
- `blocked`
- `underspecified`

The grammar is not meant to reduce intelligence. It gives intelligence a stable
surface to act through.

## Boundary Classes

Use a small boundary ladder so users can grant meaningful autonomy without
micromanaging every sprint.

| Class | Meaning | Typical approval |
|---|---|---|
| Green | docs, tests, static contracts, synthetic fixtures | autonomous if mandate allows |
| Blue | implementation inside already-approved module boundaries | autonomous if mandate allows |
| Amber | new capability scaffold, architecture track, review campaign | one envelope approval |
| Red | runtime wiring, writes, providers, real data, deployment | explicit user approval |
| Black | PHI exposure, destructive production mutation, irreversible action | hard block unless specifically authorized |

This prevents two bad extremes: a timid orchestrator that asks every few minutes
and a self-authorizing orchestrator that converts "logical next step" into
permission.

## Role Obligations

The SSDLC superstructure should remain intact whether there is one agent or
many. The harness therefore assigns obligations to roles first, then maps
available resources onto those roles.

Initial role vocabulary:

| Role | Obligation |
|---|---|
| `orchestrator` | maintain mandate, state, delegation, integration, and closeout |
| `scope_guard` | classify proposed work against mandate and boundary rules |
| `architect` | propose design, decomposition, and sequencing |
| `implementer` | produce bounded code, docs, or tests |
| `test_engineer` | define and run verification evidence |
| `security_reviewer` | perform threat modeling and abuse-case review |
| `code_reviewer` | review correctness, maintainability, and regressions |
| `docs_handover_auditor` | check documentation, handover, and closeout evidence |
| `release_gatekeeper` | verify commit, push, or release readiness |

Single-agent mapping example:

```json
{
  "resource_profile": "single_agent",
  "assignments": {
    "orchestrator": "codex",
    "architect": "codex",
    "implementer": "codex",
    "test_engineer": "codex",
    "code_reviewer": "codex",
    "security_reviewer": "codex",
    "scope_guard": "deterministic_validator"
  },
  "independence": {
    "code_reviewer": "self_review",
    "security_reviewer": "self_review"
  }
}
```

Multi-agent mapping example:

```json
{
  "resource_profile": "multi_agent",
  "assignments": {
    "orchestrator": "ariadne",
    "architect": "ariadne",
    "implementer": "codex_worker",
    "test_engineer": "ci",
    "security_reviewer": "claude",
    "code_reviewer": "deepseek",
    "docs_handover_auditor": "antigravity",
    "scope_guard": "deterministic_validator"
  },
  "independence": {
    "code_reviewer": "independent_model",
    "security_reviewer": "independent_model"
  }
}
```

The orchestrator may choose staffing. It may not delete required role
obligations because fewer resources are available.

## Worker Packet Contract

Subagents should receive structured packets, not vague delegation prompts.

Example:

```json
{
  "task_id": "sprint-012-security-review",
  "sdlc_stage": "review",
  "worker_role": "security_reviewer",
  "scope": [
    "docs/ariadne-multi-agent-ssdlc-harness-blueprint.md",
    "tests/test_orchestration_harness_replay.py"
  ],
  "authority": "read_only",
  "forbidden": [
    "implementation_changes",
    "runtime_wiring",
    "provider_calls",
    "database_writes",
    "deployment"
  ],
  "required_output": [
    "findings",
    "severity",
    "boundary_risk",
    "approval_recommendation"
  ]
}
```

Worker results should be accepted into orchestrator state only after validation:

- output schema is valid;
- scope matches the packet;
- authority was not exceeded;
- findings cite concrete files or artifacts where applicable;
- review recommendation does not claim authority it lacks.

## Orchestrator Drift Detectors

Drift should be defined as observable behavior, not user intuition.

Initial drift patterns:

- expands scope without a mandate update;
- treats a review artifact as implementation approval;
- turns docs/tests-only work into runtime wiring;
- skips threat modeling for a security-sensitive change;
- delegates vague work without role, scope, authority, or output contract;
- treats unavailable resources as permission to omit role obligations;
- hides self-review as independent review;
- continues after a stop condition;
- commits without required evidence;
- fails to update handover after a significant architecture decision;
- invents authority from precedent or "logical next step" reasoning.

Each detector should produce a structured outcome:

- `pass`
- `warn`
- `pause_required`
- `blocked`

## Evidence Model

The harness should require evidence records for stage transitions.

Example:

```json
{
  "evidence_id": "ev-verify-001",
  "stage": "verification",
  "kind": "command_result",
  "command": ["python", "-m", "pytest", "tests/test_orchestration_harness_replay.py"],
  "status": "passed",
  "scope": ["tests/test_orchestration_harness_replay.py"],
  "recorded_by": "orchestrator",
  "limitations": []
}
```

If evidence is unavailable, the harness should record the gap explicitly rather
than letting the orchestrator smooth over it.

## Initial Implementation Path

This is the proposed first safe sequence for EMR4 if Yuri continues the sidecar
track.

1. Documentation checkpoint

   Commit this blueprint. No runtime code.

2. Schema-only foundation

   Add JSON-schema-style Python dataclasses or Pydantic models for mandates,
   actions, roles, boundaries, evidence, and worker packets.

3. Synthetic replay harness

   Add fixture scenarios proving safe continuation, approval-required
   boundaries, blocked drift, missing evidence, and single-agent reduced
   independence.

4. Mock worker packet loop

   Add filesystem packet read/write helpers and mock worker result validation.
   No live worker execution.

5. Safe aggregate drift report

   Emit counts only: scenarios evaluated, actions allowed, actions blocked,
   approvals required, evidence gaps, and independence levels.

6. Optional adapter design

   Design but do not enable adapters for Codex, Claude, Antigravity, CI, or
   human review queues.

7. Explicit gate before live use

   Require separate approval before the harness can launch real agents, apply
   worker patches, move branches, commit, push, or affect EMR4 runtime work.

## EMR4 Boundary

This sidecar idea must not weaken EMR4's existing gates.

In the EMR4 repository, the blueprint opens no:

- Bernie runtime route delivery;
- provider or live-provider wiring;
- database or appointment writes;
- Access AI, memory, RAG, or GraphRAG access;
- historical diary or H15/H-series runtime access;
- frontend behavior change;
- deployment or production readiness claim;
- autonomous release authority.

The first useful EMR4 deliverable is a deterministic replay and validation
harness for the orchestration process itself, not a live multi-agent runtime.

## Open Questions

- Should the mandate ledger live in `docs/`, `orchestration/`, or a dedicated
  `.ariadne/` directory once it becomes executable?
- Should schemas be Pydantic models inside `app/services/` or a standalone
  package that can be extracted from EMR4?
- What evidence is enough for self-review in solo mode?
- Which boundaries are global defaults, and which are project-specific policy?
- How should human approvals be represented so they are auditable without
  creating friction for ordinary safe sprint progression?
- What is the minimum useful adapter for a real worker agent once mock packets
  are proven?
