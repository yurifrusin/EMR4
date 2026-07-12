# Ariadne Operating Model V2

The harness exists to prevent orchestrator drift, especially the tendency to
run successive sprints without deliberately allocating work to available
agents. It does not exist to supervise every command with another planning
cycle.

## Sprint Boundary

At the end of a sprint, executive planning authority passes to the Conductor.
The Conductor defines the next sprint, divides it into work packages, and
allocates available workers. The Orchestrator supplies product and codebase
evidence, reviews the proposal for executability and safety, and may challenge
it once. Agreement ends discussion. The Conductor publishes the final plan;
the Orchestrator then resumes executive authority for execution and integration.

This reciprocal review lets two capable models check direction without making
them co-owners of allocation or master.

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
