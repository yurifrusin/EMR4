# Ariadne Continuity Engine — Increment 1 Plan

Date: 2026-07-20

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_increment1_implementation`

## 1. Purpose

This increment establishes a durable, local continuity layer for EMR4 without
pausing or displacing the accepted Reception One product track. It borrows
Pi's inspectable branching idea but extends it into an evidence-linked directed
acyclic graph whose branches may later converge through explicit synthesis.

The result sought is not a visual graph. It is a small working engine that can
record task lineage, inherit behavioural contracts and closed boundaries,
preserve candidate harvests without promoting them to decisions, and report
continuity gaps before a descendant tranche is planned or accepted.

## 2. Authority and closed scope

Yuri authorised incremental construction of the Ariadne Continuity Engine on
2026-07-20. Increment 1 is repository-local developer tooling only.

It may:

- create one valid Codex plugin bundle containing a reusable continuity skill;
- add a standard-library Python continuity CLI;
- add a versioned JSON graph schema and a canonical EMR4 seed graph;
- implement checkpoint, fork, harvest, compare, close, show, validate and
  audit operations;
- seed only already committed non-PHI plans, acceptances, receipts, tests and
  Git coordinates from the Reception One lineage;
- record the newly observed combined-scope parity gap as an unaccepted
  continuity finding;
- add deterministic authored-synthetic fixtures and tests; and
- document the exact outcome and next increment.

It may not:

- edit the native Diary, meta-grid client, FastAPI application, GraphQL,
  OpenAPI/Pydantic contracts, database code or migrations;
- fix or reinterpret Reception One product behaviour in this tranche;
- grant authority, accept a tranche, merge a branch, move a protected ref or
  convert a candidate harvest into a durable decision automatically;
- store raw transcripts, prompts, model reasoning, passwords, credentials,
  tokens, PII, historical Diary data or protected-evidence contents;
- inspect or enumerate protected holdouts or historical Diary material;
- call a model/provider, install a subscription, use an external service or
  transmit graph content;
- add an event runtime, voice, Stage 3B, production, deployment or release
  surface; or
- install the plugin into a personal or repository marketplace in this
  increment.

## 3. Exact implementation surface

The implementation is limited to:

- `orchestration/plugins/ariadne-continuity-engine/` for the valid Codex
  plugin manifest and continuity skill;
- `scripts/ariadne_continuity.py` for the local command-line engine;
- `orchestration/continuity/ariadne-continuity-graph.schema.json` for the
  versioned machine-readable contract;
- `orchestration/continuity/emr4-continuity-graph.json` for the canonical
  metadata-only seed graph;
- `tests/test_ariadne_continuity_engine.py` and bounded authored-synthetic
  fixtures;
- this plan, a closeout and acceptance/receipt artifacts; and
- the compact live handover and orchestration topic ledger only at closeout if
  the increment passes.

No marketplace entry, MCP server, hook, visual app or transcript importer is
part of Increment 1. Those remain evidence-led later decisions.

## 4. Graph semantics

### 4.1 Nodes and relationships

Every node has a stable identifier, title, kind, lifecycle status, timestamps,
Git/task coordinates, evidence references, authority declarations, contract
evidence, decisions and unresolved gates. Evidence paths are repository-relative
metadata pointers only.

The first relationship vocabulary is:

- `builds_on` — behavioural and boundary inheritance;
- `implements` — behavioural and boundary inheritance;
- `validates` — behavioural and boundary inheritance;
- `forked_from` — branch history and boundary inheritance;
- `synthesizes` — multi-parent candidate synthesis and boundary inheritance;
- `supersedes` — disposition lineage without automatic authority; and
- `protects` — tooling/governance relationship without product-contract
  inheritance.

The graph must be acyclic. Synthesis nodes may have several parents and are
therefore more expressive than a single-parent chat tree.

### 4.2 Contract inheritance

Contracts are first-class graph records with a source node, applicability by
node kind, evidence requirements and an explanatory description. A descendant
connected through an inheriting relationship receives every applicable
ancestor contract. It must provide exact evidence or an explicit, sourced
waiver before continuity audit can pass.

A waiver is never authority by itself. It must point to a committed Yuri or Sol
acceptance artifact and remains independently reviewable.

### 4.3 Boundary inheritance

The seed graph names the currently closed API, write, event-runtime, provider,
PII, protected-evidence, historical, Stage 3B, production, deployment, release,
voice and autonomous-action boundaries. They flow through every relationship.

An opening is valid only when it names the boundary and a committed
authorization source. The engine reports missing sources; it never decides
that a source actually grants authority. Protected-evidence contents are never
stored or inspected.

### 4.4 Candidate versus accepted state

Harvest creates candidate knowledge with source and target provenance. It does
not modify the target node's decisions or status. `close --status accepted`
requires an acceptance artifact but still only records the supplied decision;
the CLI cannot create that acceptance, move Git refs or claim product success.

## 5. Command contract

All commands default to the canonical graph under the current Git worktree and
emit deterministic JSON to stdout.

- `validate` checks schema shape, identifiers, safe paths, relationship
  vocabulary, references, DAG integrity and forbidden sensitive fields.
- `audit [--node ID]` computes inherited contracts and boundaries and returns
  `passed` or `revision_required` without mutating the graph.
- `checkpoint --node-file FILE` adds a validated node and requires `--update`
  to replace an existing node.
- `fork` creates a child node with a declared parent/relation and captures
  explicit task/Git coordinates without spawning a Codex task or worktree.
- `harvest` records a candidate summary/decision with source and target
  provenance.
- `compare` reports semantic differences among selected nodes without writing.
- `close` records rejected, superseded or accepted disposition under the
  evidence rules above.
- `show` returns one node or the compact graph index.

Writes are atomic, remain inside the resolved Git worktree, fail closed on
invalid input, and never shell out or access the network.

## 6. Canonical Reception One seed

The seed graph will record, at minimum:

1. the accepted Stage 1 combined patient/practitioner/time booking-intent
   foundation;
2. the accepted provider-neutral meta-grid concept;
3. the accepted functional meta-grid client;
4. the accepted provider-free live-local integration/evaluation;
5. the active Reception One focused review; and
6. this Continuity Engine increment as a `protects` branch.

The foundation declares the combined-scope contract represented by the
existing Margaret Thompson / Dr Shera / bounded-time acceptance path. The
functional and live-local nodes deliberately do not fabricate evidence that
the newly reviewed single-request formulation passes. Their node audits must
therefore report the exact inherited contract gap while their historical
accepted claim scopes remain unchanged.

This is the first useful proof of the engine: it identifies a real continuity
obligation without rewriting an earlier acceptance or implementing the repair.

## 7. Acceptance gates

Increment 1 passes only when:

1. the plugin scaffold and manifest pass the official local plugin validator;
2. the continuity skill passes the skill quick validator;
3. the canonical graph passes structural validation;
4. cycles, missing parents, duplicate identifiers, unsafe/absolute evidence
   paths and sensitive fields fail closed;
5. applicable ancestor contracts flow through every inheriting relationship;
6. sourced contract evidence passes and absent evidence returns the exact
   `revision_required` reason;
7. closed boundaries inherit, and any claimed opening without a committed
   source returns `revision_required`;
8. checkpoint/fork/harvest/compare/close operations are deterministic and
   preserve candidate-versus-accepted semantics;
9. all writes are atomic and confined to the current Git worktree;
10. the canonical functional/live-local Reception One audit reports the known
    combined-scope gap without changing product code or acceptance status;
11. the Continuity Engine's own `protects` node does not accidentally inherit
    product behaviour contracts;
12. focused Ruff, Python compilation, deterministic tests, existing Ariadne
    preflight tests and `git diff --check` pass; and
13. the closeout states exactly what remains deferred.

## 8. Evidence and reasoning posture

- graph, schema, plan and skill: `local_continuity_design_artifact`;
- deterministic fixtures/tests: `authored_synthetic_continuity_test`;
- canonical Reception One audit: `committed_metadata_continuity_audit`.

Sol Extra High owns the frozen graph semantics because they affect future
planning and acceptance workflow. Sol High may implement and mechanically
verify the frozen contract. No implementation worker or native subagent is
used: the increment is small, tightly coupled to its schema and acceptance
meaning, and dispatch would not save a meaningful cycle.

## 9. Deferred decisions

- a visual branch-map app;
- an MCP server or direct Codex thread-tool integration;
- lifecycle hooks and automatic pre-plan enforcement;
- transcript import or summarisation;
- personal or repository marketplace installation;
- automatic Git/worktree creation;
- multi-model exploration or synthesis;
- migration of older EMR4 history beyond the canonical seed; and
- repair of the Reception One combined-scope product gap.

Each requires evidence from this increment and, where material, a fresh Yuri
decision. No deferred item is implicitly opened by this plan.
