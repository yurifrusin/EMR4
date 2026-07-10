# review-claude-fable-ariadne-harness-implementation-plan

| Item | Value |
|---|---|
| To | codex |
| From | Claude Fable |
| Status | consultant_review |
| Date | 2026-07-10 |
| Model evidence | Explicit read-only run used `claude-fable-5` |
| Inputs | `AGENTS.md`; `docs/ariadne-multi-agent-ssdlc-harness-blueprint.md`; prior Claude consultant findings packet from `claude/current` |
| Scope | Plan/review only. No code, tests, runtime wiring, live adapters, GUI, Omnigent dependency, or EMR4 runtime authority. |

## Verdict

Proceed as a passive auditor before a governor.

The blueprint is sound. The main risk is premature scope and premature
enforcement. The first valuable slice should be the Context Rehydration Gate on
a minimal schema spine, advisory-only, in a standalone top-level package.

Enforcement, live adapters, GUI, Omnigent, and any runtime authority stay behind
hard user-approval gates.

## Load-Bearing Design Decisions

1. Deterministic control of the orchestrator

   Determinism must classify observable artifacts: paths, diffs, refs, command
   arrays, mandate files, checkpoint files, evidence records, and git state.
   It must not trust the orchestrator's self-declared intent.

   Non-optionality eventually comes from existing protocol choke points such as
   `scripts/agent_worktrees.py submit`, `handoff`, and `realign`; those hooks
   must be advisory first and enforced only later, check by check.

2. Context rehydration gate

   This is the MVP. It should be a read-only inspector with outcomes limited to
   `passed` and `pause_required`, plus per-reason remediation strings.

   Compaction summaries are convenience text. Authority comes from git state,
   mandate files, checkpoint files, and evidence ledgers.

3. SSDLC stage model

   Stages are data, based on the blueprint's intake/design/threat-model/
   implementation/verification/review/integration/closeout spine. Transitions
   require evidence.

   Evidence records should carry a git tree or diff fingerprint so stale
   evidence is detectable.

4. Mandate ledger

   Mandates should live under a coordination surface such as
   `orchestration/harness_mandates/` and be schema-validated.

   The orchestrator may not widen a mandate from chat history, momentum, or a
   "logical next step". Only a user-approved mandate file change widens it.

5. Role elasticity

   Roles are contracts. Agents are resources.

   A `ResourceProfile` maps roles to resources. Missing resources reduce
   independence, recorded as `self_review`; they never delete required role
   obligations. Self-review can never clear a Red boundary.

6. Codex-first, platform-neutral

   The harness core should be a portable Python package and CLI. Adapters own
   OS/tool-specific behavior. The first useful adapter is filesystem/mock, not a
   live agent launcher.

   Add a portability lint test: no `import app` in the harness core, no shell
   strings as command contracts, and `pathlib` for paths.

7. EMR4-first, then extract

   Put the core in a top-level `orchestration_harness/` package, not
   `app/services/`, so later extraction is a directory move rather than clinical
   dependency surgery.

   EMR4 policy should be passed as data. Extraction should wait until the
   harness saves or improves at least one real EMR4 sprint.

8. No-go gates

   Every advisory-to-enforcing promotion, live worker adapter, harness git
   mutation, GUI, Omnigent dependency, or runtime authority requires separate
   explicit Yuri approval. Existing EMR4 gates remain strictly dominant; the
   stricter gate wins.

## Implementation Sequence

Each sprint below is Green unless marked otherwise.

### S0 - Docs Checkpoint

Preserve this consultant plan in the repo review surface and add a small
glossary later distinguishing:

- Ariadne harness;
- Bernie interpretation harness;
- H-series historical-diary gates;
- EMR4 worker handoff protocol.

Gate: explicit release for S1.

### S1 - Schema Spine

Add a top-level `orchestration_harness/` package with only:

- `Mandate`;
- `BoundaryClass` from Green to Black;
- `ActionClassification` values:
  `allowed`, `allowed_with_evidence`, `requires_user_approval`, `blocked`,
  `underspecified`.

Tests:

- JSON round-trip fixtures;
- portability lint;
- current sidecar mandate validates as data.

Gate: tests green, lint green, and a real mandate expressed as data.

### S2 - Context Rehydration Gate MVP

Add:

- `orchestration_harness/rehydration.py` with pure functions;
- `scripts/ariadne_context_rehydration_check.py` as a thin CLI;
- fixtures for clean state, dirty worktree, missing mandate, missing checkpoint,
  and unclassified next action.

Git state should be injected as data in tests. The first implementation should
not mutate branches, write commits, or launch agents.

Gate: fixture tests pass and the gate runs at the start of at least two real
sprints with zero false `pause_required` outcomes.

### S3 - Boundary And Action Classifier, Advisory

Classify proposed actions from observable artifacts into boundary class and
verdict. This remains log-only.

Add `Evidence` schema with:

- state fingerprint;
- command array;
- scope;
- recorded-by;
- limitations;
- freshness check.

Gate: replay agreement against at least 15 hand-labelled real EMR4 actions from
past closeouts.

### S4 - SSDLC Stage Model And Drift Corpus

Add a replay-only stage-transition validator and labelled drift corpus harvested
from real repo history.

Use known protocol-alert corrections and gate-repair sprints as positive drift
examples, and clean closeouts as negative examples.

Detector labels may include:

- `pass`;
- `warn`;
- `pause_required`;
- `blocked`.

At this stage they are labels only, not enforced blocks.

Gate: detectors separate historical drift from known-good sprints with useful
precision.

### S5 - Role Elasticity, Worker Packets, Safe Report

Add:

- `Role`;
- `ResourceProfile`;
- independence labels such as `self_review`, `independent_model`,
  `human_review`, and `tool_verified`;
- `WorkerPacket`;
- filesystem packet helpers;
- mock worker result validation;
- safe aggregate report.

Tests:

- valid packet accepted;
- invalid scope rejected;
- authority overreach rejected;
- missing citations rejected where required;
- report is counts-only and payload-free.

Gate: H50/H51-style report safety assertion passes.

### S6 - Advisory Choke-Point Hook

Amber. Requires one envelope approval.

Run the harness at `agent_worktrees.py` submit/handoff points in advisory mode
only. It may log warnings but must not block.

Gate to enforcement: explicit approval plus measured advisory agreement.

## Hard-Gated, Not Scheduled

These are not part of the initial implementation sequence:

- enforcement promotion;
- live worker adapter;
- GUI;
- Omnigent dependency;
- harness-owned git mutation;
- EMR4 runtime authority;
- provider calls;
- database writes;
- historical diary/H15/H-series runtime use.

Live worker adapter work requires a threat-model artifact first. GUI and
Omnigent must remain optional operator/adaptor layers, never the authority
layer.

## Verification Strategy

All initial tests should be deterministic, provider-free, network-free, DB-free,
and live-agent-free:

- schema round trips;
- portability lint;
- rehydration fixtures with exact reason/remediation assertions;
- classifier replay corpus;
- drift corpus separation;
- mock packet accept/reject matrix;
- payload-free report snapshots;
- real-sprint dry-run notes recorded in closeouts as gate evidence.

## Meta-Risk

The harness track itself can become the drift.

Time-box it against real EMR4 payoff: it must prevent a real drift, reduce user
permission fatigue, or improve a real handoff within a small number of sprints,
or be parked.
