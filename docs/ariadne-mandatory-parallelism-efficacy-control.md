# Ariadne mandatory parallelism-efficacy control

Date: 2026-08-14

Timestamp: 2026-08-14T09:50:00+10:00 (Australia/Brisbane)

Status: implemented

## Problem

Worker allocation was already encouraged by policy, but a fresh or compacted
task window could still fall back to solo serial work without making that
choice visible. A preference in prose did not create a fail-closed continuity
obligation.

## Control

Every configured Ariadne continuation event now requires a typed
`parallelism_assessment` bound to the active operation. The assessment must
give separate dispositions for:

1. `deepseek_flash` — bounded separable implementation, tests or mechanical
   artifacts;
2. `gemini_verifier` — independent read-only veto or explicitly reserved veto;
3. `native_subagents` — parallel read-only analysis or bounded separable
   artifacts.

Each lane records disposition, expected leverage, a distinct rationale and any
owned work package. The assessment also records parallel packages, serial
constraints and reassessment triggers. A continuation receipt is
`revision_required` when the assessment is missing, not bound to the active
operation, omits a lane, declares active work without a package, lacks
reassessment triggers, or provides neither useful parallel work nor an
explicit serial constraint.

This makes consideration mandatory, not dispatch. Serial execution remains
correct for tightly coupled mutable state, tiny work whose packet/review cost
exceeds its value, or work that must pass a deterministic gate before an
independent veto. Those reasons must now survive compaction and task-window
restoration in the receipt itself.

## Planning and closeout

Every tranche plan must record the expected DeepSeek, Gemini and native-agent
dispositions, separable packages, dependency ordering and reassessment
triggers. Every closeout must compare expected with actual worker use and
explain substitutions or non-use. Material recovery triggers a reassessment;
the initial allocation is not treated as immutable when the work separates or
couples differently in practice.

## Authority boundary

The assessment does not allocate acceptance, integration, baton or protected-
ref authority to a worker. It cannot manufacture a useful package, override
the worker-economy rule, parallelize PostgreSQL-schema-owning pytest processes,
or bypass deterministic admission before Gemini. It adds no provider, data,
runtime, command, deployment or release authority.
