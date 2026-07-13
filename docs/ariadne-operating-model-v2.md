# Ariadne Operating Model V2

Status: compatibility narrative amended by Operating Model V3 on 2026-07-14.
The machine-readable authority is
`orchestration/harness_settings/operating_model.yaml`.

Routine bounded sprints are now planned and allocated directly by the protected
Sol orchestrator. DeepSeek Pro is an optional compact consultant when a genuine
architecture, programme, material-allocation, or repeated-failure question has
clear leverage. This change avoids duplicating a large coordinator plan and a
second Sol acceptance pass merely to allocate ordinary implementation lanes.

The harness exists to prevent orchestrator drift, especially the tendency to
run successive sprints without deliberately allocating work to available
agents. It does not exist to supervise every command with another planning
cycle.

## Sprint Boundary

At the end of an ordinary bounded sprint, the protected Sol orchestrator defines
the next sprint, divides it into work packages, and allocates available workers.
It may select an independent Conductor consultation when a configured leverage
trigger applies. In that selected mode, the Conductor publishes the consulted
plan and Sol retains protected integration authority.

Optional reciprocal review lets two capable models check difficult direction
without making them co-owners of protected master.

## Within A Sprint

The Orchestrator waits for workers, retries the same lane, repairs transport,
selects commands, manages worktrees, runs tests, reviews evidence, and
integrates accepted work. These actions do not return to the Conductor or user.

The Conductor re-enters only when sprint scope, worker assignment/ownership, or
acceptance criteria must change, or when the sprint closes and the next sprint
must be planned.

## Verification

Deterministic schema, fingerprint, resource-limit, ownership, and workspace
checks always run. An independent LLM verifier is optional and risk-triggered:
new authority, ambiguous boundaries, material Conductor-Orchestrator
disagreement, resource exceptions, or an authority/ownership drift signal.
Ordinary plans, retries, and transport corrections do not require it.

## Execution Controls

Wall-clock deadlines and monetary caps remain available generic capabilities
but are inactive in the current profile. Progress observation is preferred to
elapsed time. A live worker may continue while it is making observable
progress; intervention is an Orchestrator execution judgment, not a new sprint
planning event.

## Continuous Sprint Engine

Sprint closeout is not a conversational stopping point. Sol closes the sprint,
hands planning authority to Fable, reviews the resulting next-sprint plan,
runs deterministic checks and any risk-triggered independent review, then
executes. This cycle continues sprint after sprint without asking the user to
say "continue". It stops only for an explicit user stop or a genuine
undelegated decision boundary.

Accepted worker artifacts, harness corrections, bounded integrations, and
sprint closeouts are committed and pushed regularly by Sol, with
`handoff/current` advanced. Worker agents never push master. Continuous
execution must not mean an indefinitely dirty integration worktree.
