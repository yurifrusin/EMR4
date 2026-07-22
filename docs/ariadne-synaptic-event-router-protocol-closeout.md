# Ariadne Synaptic Event Router - Protocol Tranche Closeout

Date: 2026-07-22

Result: `ariadne_synaptic_event_router_protocol_pass`

Owner: GPT Sol Extra High

## Outcome

The bounded repository-local Synaptic Event Router protocol tranche passes. It
extends the accepted Sandbox DAG exchange grammar with deterministic
authored-synthetic event-to-scope steering while attaching no database, event
feed, product API, model, provider, container, mailbox runtime or command.

The accepted predecessor remains intact: its 13 immutable nodes, 13 typed
exchanges, bilateral direct sandbox data link, forward-only context round trip,
restart lineage, fan-out/fan-in and terminal human-authority gate validate
unchanged. The new notice is a router-to-node control-plane exchange and does
not relax the ban on sandbox-peer control messages.

## What was proved

- A static router policy and node lease must bilaterally agree on router
  instance, `control` channel, `scope-change-notice` kind, event/schema and
  steering frame.
- One authored-synthetic committed `diary.appointment_rescheduled` event fans
  out to two intersecting node leases without becoming command authority.
- Eleven ordered route attempts produce exactly two minimal mailbox notices and
  nine suppressions: replay, cross-practice, non-intersection, superseded lease,
  expiry, non-newer revision, sensitivity, undeclared frame and undeclared event.
- A same-generation lease revision may only narrow scope. Peer, channel, kind,
  frame, practice, principal, mailbox, checkpoint and policy changes require a
  later container generation and higher immutable policy revision.
- Every notice carries the predecessor grammar's workflow/graph revision,
  immutable sender/recipient, correlation, provenance and freshness fields.
- Fresh-read grants are exact practice/principal/role/action/resource,
  event/revision and expiry descriptors with `execution_enabled: false` and
  `returns_data: false`.
- `reconcile-at-boundary` stops at fresh-read need. `cancel-and-supersede`
  creates a later immutable attempt with exact checkpoint lineage; stale earlier
  completion is rejected.
- The compiler deterministically emits source-hashed, default-deny start-up,
  subscription and restart-policy manifests. Five statically eligible leases
  compile and four superseded, expired or unilateral declarations are denied.

## API Spine and security result

Boundary classification:
`non_executing_async_event_scope_routing_and_manifest_protocol`.

The event remains a typed committed signal, not a command. Practice and
integration-principal coordinates are explicit, the mailbox deduplication key
provides the inert idempotency contract, fresh authorised reads remain separate,
GraphQL remains read-only, and REST/OpenAPI remains the future command boundary.
The manifests are declarative inputs, not policy executors. No
`docs/api-spine/` change was needed; its existing artifact population passes.

The threat-model delta covers cross-practice steering, ambient/unilateral
delivery, scope amplification, stale overwrite, replay, revision rollback,
payload smuggling, sensitivity escalation, grant laundering, event-to-command
escalation, manifest execution, hidden runtime coupling and evidence privacy.

## Artifacts

- `docs/ariadne-synaptic-event-router-protocol-plan.md`
- `docs/ariadne-synaptic-event-router-protocol-design.md`
- `docs/security/ariadne-synaptic-event-router-threat-model-delta.md`
- `scripts/ariadne_synaptic_event_router.py`
- `orchestration/continuity/ariadne-synaptic-event-router.schema.json`
- `orchestration/continuity/ariadne-synaptic-event-router-example.json`
- `orchestration/continuity/ariadne-synaptic-event-router-dry-run-manifests.json`
- `orchestration/continuity/ariadne-synaptic-event-router-evidence.json`
- `tests/test_ariadne_synaptic_event_router.py`
- `orchestration/agent_inbox/codex/ariadne-synaptic-event-router-protocol-sol-acceptance.md`

## Verification

- focused Synaptic Event Router suite: 15 passed, 0 failed;
- combined router, predecessor Sandbox DAG, Continuity, Compass, orchestrator,
  operating-model, API Spine and handover population: 106 passed, 0 failed;
- semantic protocol validation and Draft 2020-12 JSON Schema: passed;
- route, manifest and evidence exact deterministic comparisons: passed;
- API Spine artifact compatibility: passed;
- Ruff and Python compilation: passed;
- JSON parsing and `git diff --check`: passed.

The two warnings are existing Starlette and Google GenAI dependency
deprecations and are unrelated to this tranche.

Evidence label:
`authored_synthetic_repository_local_non_executing`.

No browser, FastAPI, PostgreSQL, event-feed, container or provider evidence was
run or claimed because none is authorised or present.

## Allocation and review

Sol Extra High owned architecture, implementation, tests, acceptance and
protected integration. No implementation worker or native subagent was used
because the protocol, schema, negative paths and generated artifacts are tightly
coupled. No external independent model review was used because Yuri explicitly
closed model connections for this tranche. The result therefore claims
deterministic local Sol acceptance, not a fresh independent veto.

## Preserved gates and next decision

PostgreSQL, an outbox or event-feed adapter, product reads, an operational scope
registry, persistent mailbox, listener, broker, retry/dead-letter worker,
retention policy, additional event family, model, container, command, PII,
protected/historical data, Stage 3B, production, deployment, release and
autonomous action remain closed.

Return the baton to Yuri. If Yuri elects to continue, the smallest runtime
candidate is a separately authorised adapter to only the existing default-off
local `diary.appointment_rescheduled` feed, with a fresh runtime threat model,
authentication, durable deduplication, persistence, failure and retention
decision. This closeout grants none of that authority.
