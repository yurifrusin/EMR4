# Ariadne Sandbox DAG — First Fork Closeout

Date: 2026-07-22

Result: `ariadne_sandbox_dag_fork_pass`

Owner: GPT Sol Extra High

## Outcome

The first deliberate `forked_from` branch in the Ariadne Continuity Engine
passes. It explores a synaptic DAG of isolated workers without changing the
accepted Reception One product journey or attaching a workflow, model,
container, database or command actuator.

The central refinement came from Yuri during implementation: the orchestrator
is the control plane, not a compulsory relay for all data. A sandbox may send a
typed data result directly to a peer only when both containers' immutable
start-up policies name the peer instance, channel and frame. The canonical
authored-synthetic trace exercises one such availability-to-ranking link.

## What was proved

- Thirteen immutable nodes exchange thirteen typed messages in a deterministic
  DAG.
- A missing context frame travels through an explicit causal sequence:
  leaf request, later orchestrator, declared human context source, later
  orchestrator grant and later leaf attempt.
- One orchestrator fan-out leads to separate availability and policy work.
- Availability candidates travel directly across one bilaterally declared
  sandbox peer edge rather than through the orchestrator.
- Ranked candidates and authority constraints converge at an explicit join.
- Evidence and candidate outputs are separate. The candidate terminates at one
  `awaiting-human-authority` gate with no outgoing edge.
- Communication policy is immutable within a container generation. A policy
  amendment is valid only with a later generation, higher revision and exact
  `restarted_from` lineage.
- Unknown peers, unilateral rules, peer control messages, cycles, undeclared
  frames/properties/capabilities, stale grants, unsafe evidence, sensitive
  content and execution states fail closed.

## Artifacts

- `docs/ariadne-sandbox-dag-fork-plan.md`
- `docs/ariadne-sandbox-dag-protocol-design.md`
- `scripts/ariadne_sandbox_dag.py`
- `orchestration/continuity/ariadne-sandbox-dag.schema.json`
- `orchestration/continuity/ariadne-sandbox-dag-example.json`
- `orchestration/continuity/ariadne-sandbox-dag-fork-evidence.json`
- `tests/test_ariadne_sandbox_dag.py`
- `orchestration/agent_inbox/antigravity/ariadne-sandbox-dag-fork-final-review.md`
- `orchestration/agent_inbox/codex/ariadne-sandbox-dag-fork-sol-acceptance.md`

The canonical continuity graph records `ariadne-sandbox-dag-fork` as an
accepted exploration related to `ariadne-compass-increment2` by `forked_from`.
The Compass revision was advanced only to bind the newer graph revision. Its
seven-step Reception One journey, current product node, decision horizon and
Yuri-owned decisions are unchanged.

## Verification

- focused sandbox-DAG tests: 12 passed, 0 failed;
- combined sandbox-DAG, Continuity, Compass, preflight, operating-model and
  handover tests: 55 passed, 0 failed;
- protocol semantic validation and JSON Schema: passed;
- continuity graph validation and sandbox-fork node audit: passed;
- Compass validation and exact generated report comparison: passed;
- Ruff and Python compilation: passed;
- plugin and skill validation: passed;
- JSON parsing and `git diff --check`: passed; and
- fresh Gemini 3.5 Flash High veto: `DECISION: pass`, no material finding.

The two test warnings are existing dependency deprecations from Starlette and
Google GenAI imports; neither is caused by this tranche.

Evidence label:
`repository_local_authored_synthetic_protocol_trace`.

No browser, FastAPI or PostgreSQL evidence was needed because no product or
runtime surface changed.

## Authority and boundary result

The CLI exposes only `validate` and `trace`. Static inspection rejects network,
subprocess, database and product imports. Capability and communication-policy
records are inert descriptors; they neither create a container nor enforce a
real network policy.

No API, REST/OpenAPI, GraphQL, FastAPI, database, migration, appointment write,
event runtime, provider, PII, protected/historical evidence, Stage 3B,
production, deployment, release or autonomous-action authority opened.

## Allocation

Sol Extra High owned architecture, implementation and acceptance because the
protocol defines possible future authority semantics and was tightly coupled to
its schema and negative-path tests. No implementation worker or native subagent
was used. Gemini 3.5 Flash High supplied the required fresh independent veto and
received no edit, acceptance, integration or protected-ref authority.

## Deferred decisions

This result does not authorise a Plan Compiler, workflow executor, real model or
container, network enforcement, policy restart, token/sensitivity broker,
database context source, EMR read or command, practice-manager approval UI,
provider, production, deployment or release.

If Yuri wishes to continue this branch, the next bounded candidate is a dry-run
policy compiler that translates the accepted graph into inspectable container
start-up manifests and restart diffs without starting anything. That is not
authorised by this closeout.
