# Ariadne Bounded Cognitive Work Cell and Proofreader Gate - Protocol Closeout

Date: 2026-07-23

Result: `ariadne_bounded_cognitive_work_cell_protocol_pass`

Owner: GPT Sol Extra High

## Outcome

The bounded repository-local Bounded Cognitive Work Cell and Proofreader Gate
protocol tranche passes. It formalises Yuri's coarse-cognition, fine-authority
design: one agent-eligible but unoccupied work cell may perform a coherent
bounded booking-availability task and emit several typed drafts, while a pure
deterministic proofreader is the only egress route.

The proof is authored-synthetic and non-executing. It attaches no model,
provider, real container, PostgreSQL connection, event feed, product API, live
mailbox, human-gate UI or command adapter.

## What was proved

- Node, topological leaf, execution class, container posture and agent
  eligibility are independent concepts. Three deterministic leaves are
  intentionally uncontainerised; the one agent-eligible interior work cell has
  `agent_attached: false` and `container_started: false`.
- The node-granularity rule is `coarse-cognition-fine-authority`. Functional
  miniaturisation is not required; splits occur at practice/principal,
  sensitivity/purpose, freshness/transaction, fact-source, irreversible-action,
  persistence/idempotency or privacy-co-presence boundaries.
- One primary work-cell attempt emits five typed drafts: UX projection, human
  review, audit evidence, orchestrator outcome and advisory explanation.
- The proofreader deterministically checks exact port/schema, scope,
  provenance, freshness, authority, grounding, candidate consistency and
  atomic cross-output consistency in a fixed order.
- All eight verdict paths pass: downstream and human release, both safe-repair
  variants, schema and grounding retry, stale-context rejection and immediate
  authority rejection.
- Safe repair is limited to duplicate removal and stable sorting of opaque
  reference lists. Two repairs retain immutable original hashes and distinct
  derived-frame hashes; no repair invents a reference, resolves ambiguity,
  refreshes context or elevates authority.
- Retry uses immutable later attempts and a two-attempt same-reason budget.
  Repeated unknown-slot failure aborts only the affected edge.
- Stale context binds an inert fresh-read grant, advances attempt/container
  generation and policy revision through exact supersession lineage, remains
  `awaiting-fresh-context`, and rejects the stale earlier completion.
- The UX/human-review atomic group is all-or-none. A field mismatch or an
  independently rejected member withholds every grouped edge.
- Human routing is a verified success path, but the gate is inert, cannot
  rehabilitate a rejected frame and has no command authority. Future approval
  remains evidence requiring separately authorised backend revalidation.
- Compiled manifests are exact, source-hashed, default-deny and non-executing.

## Canonical evidence

The authored-synthetic document contains:

- 7 nodes;
- 6 bounded input frames;
- 5 typed output ports;
- 11 immutable work-cell attempts;
- 15 draft frames;
- 10 proofreader cases;
- 8 released hashed edges;
- 2 immutable repair receipts; and
- 1 inert fresh-read grant.

The accepted Sandbox DAG remains unchanged at 13 nodes and 13 typed exchanges.
The accepted Synaptic Event Router protocol also validates unchanged.

Evidence label:
`authored_synthetic_repository_local_non_executing`.

## API Spine and security result

Boundary classification:
`non_executing_agent_context_egress_verification_and_human_gate_protocol`.

The work cell receives typed minimal source-labelled context rather than API or
database access. Identity, availability, policy and freshness remain supplied
facts. Candidate and advisory drafts never become authoritative facts or
commands. GraphQL remains read-only and unused; REST/OpenAPI remains the future
command boundary and unused. Human confirmation remains evidence for later
backend revalidation. No `docs/api-spine/` artifact changed.

The threat-model delta covers topology/isolation confusion, premature
containerisation, silent future agentisation, schema-shaped fabrication,
authority and stale-fact laundering, semantic repair, evidence rewrite,
partial atomic release, retry loops and injection, grant laundering, stale
completion, human-gate bypass, advisory escalation, sensitive aggregation,
payload smuggling, manifest execution and evidence overclaim.

## Artifacts

- `docs/ariadne-bounded-cognitive-work-cell-protocol-plan.md`
- `docs/ariadne-bounded-cognitive-work-cell-protocol-design.md`
- `docs/security/ariadne-bounded-cognitive-work-cell-threat-model-delta.md`
- `scripts/ariadne_bounded_cognitive_work_cell.py`
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell.schema.json`
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-example.json`
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-dry-run-manifests.json`
- `orchestration/continuity/ariadne-bounded-cognitive-work-cell-evidence.json`
- `tests/test_ariadne_bounded_cognitive_work_cell.py`
- `orchestration/agent_inbox/codex/ariadne-bounded-cognitive-work-cell-protocol-sol-acceptance.md`

## Verification

- focused Bounded Cognitive Work Cell suite: 20 passed, 0 failed;
- combined work-cell, Event Router, Sandbox DAG, Continuity, Compass,
  orchestrator, operating-model, API Spine and handover population: 126 passed,
  0 failed;
- semantic protocol validation and Draft 2020-12 JSON Schema: passed;
- proofreader, manifest and evidence exact deterministic comparisons: passed;
- API Spine artifact compatibility: passed;
- Ruff and Python compilation: passed; and
- JSON parsing and `git diff --check`: passed.

The draft PR's first CodeQL pass identified one high-severity diagnostic-echo
path and one unused local assignment. The approved bounded repair removed the
dead assignment and changed the public trace from per-document identifiers and
rejection details to fixed verdict labels plus aggregate edge/repair counts.
The repaired focused/combined populations and GitHub CodeQL checks pass.

The two warnings are existing Starlette and Google GenAI dependency
deprecations and are unrelated to this tranche.

No browser, FastAPI, PostgreSQL, event-feed, container, mailbox or provider
evidence was run or claimed because none is authorised or present.

## Allocation and review

Sol Extra High owned architecture, implementation, tests, acceptance and
protected integration. No implementation worker, native subagent or external
model reviewer was used because the authority semantics, schema, verifier and
negative traces are tightly coupled and Yuri explicitly closed model/provider
connections. The result claims deterministic local Sol acceptance, not a fresh
independent veto.

## Preserved gates and next decision

PostgreSQL, event feeds, product APIs, GraphQL/REST changes, live context reads,
models, providers, real containers, live mailboxes, persistent retry, human-gate
UI, signed approval, appointment commands, PII, protected/historical evidence,
Stage 3B, production, deployment, release and autonomous action remain closed.

Return the baton to Yuri. If Yuri elects to continue this architecture branch,
the smallest separately authorised descendant is an in-memory scripted work-cell
rehearsal using only pre-authored synthetic drafts. It could exercise the
proofreader/control-plane transition grammar over multiple immutable attempts
without a model, real container, product adapter, live mailbox or command. This
closeout grants none of that authority.
