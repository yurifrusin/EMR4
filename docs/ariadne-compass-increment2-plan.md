# Ariadne Compass — Increment 2 Plan

Date: 2026-07-21

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_compass_increment2`

## 1. Purpose

Yuri authorised construction of Ariadne's Compass after identifying a real
programme-navigation problem: EMR4 work is progressing through accepted,
well-evidenced tranches, but the relationship between the current tranche, the
Reception One programme and the wider EMR4 destination is not continuously
visible in a concise human form.

Increment 2 adds a read-only navigation layer over the accepted Continuity
Engine. It must answer:

1. What larger product outcome are we pursuing?
2. Where is the active product track inside the EMR4 programme?
3. What sequence of capabilities led to the current position?
4. What did the latest accepted work prove?
5. What does that work unlock, and what does it explicitly not solve?
6. Which next directions are candidates, deferred or blocked?
7. Which choices belong to Yuri rather than an agent or workflow?

The Compass is a compass, not an autopilot. It may describe and validate the
decision horizon; it may not select a tranche, allocate a worker, execute a
plan, grant authority or mutate product state.

## 2. Authority and boundaries

This increment may:

- add a versioned, repository-local Compass schema and canonical EMR4 map;
- add a standard-library Python validator and report renderer;
- reuse only committed non-PHI plans, closeouts, acceptances and continuity
  node identifiers;
- render deterministic JSON and plain-language Markdown to stdout;
- add a `protects` continuity node for the Compass increment;
- add focused authored-synthetic tests and evidence; and
- update the reusable Ariadne plugin guidance, live handover and continuity
  ledger if acceptance passes.

It may not:

- choose or authorise the next EMR4 or Reception One product tranche;
- create a task, agent, worktree, worker packet, PR, commit, merge or Git ref;
- call an LLM/provider from the Compass runtime;
- read transcripts, prompts, protected evidence, historical Diary material,
  PII, credentials or secrets;
- edit the Diary, FastAPI, GraphQL, OpenAPI, database, migrations, event runtime
  or production configuration;
- execute an EMR command, appointment write, deployment or release; or
- represent the current Reception One subgraph as a complete map of every
  EMR4 domain.

API, appointment-write, autonomous-action, event-runtime, provider, PII,
protected-evidence, historical-diary, Stage 3B, production, deployment,
release and voice boundaries remain closed.

## 3. Exact implementation surface

The implementation is limited to:

- `scripts/ariadne_compass.py`;
- `orchestration/continuity/ariadne-compass.schema.json`;
- `orchestration/continuity/emr4-compass.json`;
- `orchestration/continuity/emr4-continuity-graph.json` for one `protects`
  tooling node only;
- `tests/test_ariadne_compass.py` and the existing bounded Continuity Engine
  tests where compatibility requires it;
- `orchestration/plugins/ariadne-continuity-engine/skills/ariadne-continuity/SKILL.md`;
- this plan, the generated-current-report evidence, closeout, acceptance and
  mandatory Ariadne receipts; and
- `AGENTS.md` and the continuity topic ledger only after acceptance.

The tool accepts the canonical graph and Compass map by default. `validate`
checks their relationship. `show --format json|markdown` renders the current
programme position without writing either source.

## 4. Compass contract

### 4.1 Programme hierarchy

The canonical map names:

- the EMR4 product north star;
- the active Reception One programme and its master-plan phase;
- the latest accepted product position; and
- the limit that the current continuity population is not yet an exhaustive
  map of all EMR4 domains.

Every prose claim points to an existing repository-relative evidence file.

### 4.2 Journey

The journey is an ordered list of accepted continuity nodes. Every non-root
step names a real earlier journey node as its lineage parent through an
inheriting graph relationship; a map cannot invent lineage merely to turn
product chronology into one artificial chain. Each step supplies a short
strategic role and a plain-language outcome.

The initial journey is:

`Stage 1 authority foundation → meta-grid concept → functional client →
live-local integration → combined-scope proof → committed-reschedule event →
availability reconciliation`.

### 4.3 Current position

The current position records:

- the latest accepted product node;
- why that capability was the relevant next proof;
- the accepted outcome;
- what it unlocks;
- what it does not solve; and
- its evidence sources.

The validator requires this node to exist, be accepted, appear as the last
journey step and pass the Continuity Engine audit. A stale or continuity-failing
position returns `revision_required`.

### 4.4 Decision horizon

Every horizon item is explicitly one of `candidate`, `deferred` or `blocked`.
It states the strategic question, why it might matter, prerequisites, boundary
changes it would require and evidence. No candidate is rendered as a decision.

The initial product horizon contains only the two choices already named by the
accepted availability closeout:

- Reception One visual/interaction synthesis; or
- a separately authorised review for another typed Diary event family.

The map also records Compass workflow-executive maturation as a programme-
support candidate, separate from the product decision horizon.

### 4.5 Yuri-owned decisions

The map explicitly identifies questions that must return to Yuri. A Compass
report cannot convert a candidate, deferred item or unresolved question into an
accepted plan.

## 5. Fail-closed validation

Validation must reject:

- an unknown schema or project;
- a Compass graph revision that differs from the loaded graph;
- unsafe, absolute, missing or external evidence paths;
- forbidden sensitive field names anywhere in the map;
- duplicate journey or decision identifiers;
- an unknown, non-accepted, unauditable or non-terminal current node;
- journey adjacency without an inheriting graph relationship;
- a decision item without status, prerequisites, boundary changes or evidence;
- an unknown closed-boundary identifier; and
- empty strategic summaries, outcomes, limitations or user decisions.

The renderer does not infer missing prose and never consults the network.

## 6. Human report

The Markdown view must lead with a short orientation statement and contain:

- North star;
- Programme position;
- Journey so far;
- Current position;
- What this unlocks;
- What it does not solve;
- Continuity and authority status;
- Decision horizon;
- Yuri-owned decisions; and
- Map limits.

The output must remain readable without understanding graph vocabulary. IDs,
schema versions and exact evidence pointers remain available in the JSON view.

## 7. Acceptance

Increment 2 passes only when:

1. the schema and canonical map validate;
2. the current node audit passes and all inherited contracts remain satisfied;
3. journey order and every declared lineage parent are mechanically consistent;
4. stale revisions, unsafe references, sensitive fields, unknown boundaries,
   non-accepted current positions and fabricated lineage fail closed;
5. JSON and Markdown reports are deterministic and read-only;
6. the Markdown report answers all seven purpose questions in plain language;
7. focused Compass and inherited Continuity/Ariadne tests, compilation, Ruff,
   JSON parsing and `git diff --check` pass;
8. a fresh independent Gemini veto finds no material navigation, authority,
   provenance or evidence-integrity defect;
9. Sol records bounded acceptance and an exact closeout; and
10. a check-gated PR integrates and protected refs realign.

No browser, backend or PostgreSQL evidence is required because this increment
adds no UI or product runtime. Its evidence label is
`repository_local_metadata_navigation`.

## 8. Allocation and reasoning

Sol Extra High owns the programme semantics, map boundary and acceptance
meaning. Sol implements the small, tightly coupled schema/validator/renderer
directly; a worker packet would not save a meaningful cycle. No native
subagent or implementation worker is assigned.

A fresh Gemini 3.5 Flash review through Antigravity is required over the clean
candidate because the Compass will influence future planning. Gemini receives
no edit, acceptance, integration, baton or protected-ref authority.

## 9. Deferred executive work

This increment does not add:

- automatic pre-plan hooks;
- a typed executable sprint plan;
- model selection or LLM Conductor invocation;
- worktree, test, browser, reviewer, PR or Git execution;
- a visual branch-map application; or
- product-command capabilities.

The report generated here will provide the evidence needed to decide whether a
later dry-run Plan Compiler and, after that, a capability-brokered Workflow
Executor would materially reduce EMR4 coordination cost without obscuring Yuri's
authority.
