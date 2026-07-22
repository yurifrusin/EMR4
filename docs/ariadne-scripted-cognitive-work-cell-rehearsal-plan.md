# Ariadne Scripted Cognitive Work Cell Rehearsal - Tranche Plan

Date: 2026-07-23

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_in_memory_scripted_rehearsal`

## 1. Purpose

Yuri authorised the smallest recorded descendant of the accepted Bounded
Cognitive Work Cell and Proofreader Gate protocol: a repository-local,
in-memory scripted rehearsal using only pre-authored synthetic inputs and
drafts.

The tranche will exercise the already accepted proofreader/control-plane
transition grammar over several immutable work-cell attempts. It will show what
happens after deterministic verification: verified release, inert human-gate
routing, allowlisted repair, bounded later-attempt request, repeated-failure
edge abortion, stale-context supersession and authority abortion.

The rehearsal executes a finite deterministic state machine in local process
memory. It does not execute product work, generate a draft, attach an adaptive
agent, start a container, perform a read, persist a mailbox or call a command.

Exact target result:
`ariadne_scripted_cognitive_work_cell_rehearsal_pass`.

## 2. Authority and inherited boundaries

This tranche may:

- add one standard-library in-memory rehearsal runner which imports and reuses
  the accepted work-cell validator and proofreader;
- add one Draft 2020-12 schema and one finite authored-synthetic script whose
  attempt, draft, verifier-case, retry, grant and supersession references all
  resolve into the accepted canonical work-cell document;
- load those two repository artifacts into memory and advance a fixed ordered
  step tape;
- create immutable in-memory transition records and a deterministic hash chain;
- record verified-edge envelopes, minimal correction requests, inert fresh-read
  grant bindings, explicit supersession, edge abortion and inert human-gate
  delivery as process-local evidence;
- add deterministic positive and negative tests and committed expected evidence;
  and
- register a metadata-only Continuity descendant after every acceptance gate
  passes.

It may not:

- invoke, simulate or select a model, provider, adaptive agent, plugin, external
  service or worker;
- start or configure a real container, network sandbox, server, browser,
  background process, subprocess actuator, thread, timer or scheduler;
- connect to PostgreSQL, a database, event feed, outbox, broker, product API,
  GraphQL, REST/OpenAPI, FastAPI, filesystem mailbox or command adapter;
- fetch, generate, infer, rewrite or persist an input frame, draft, attempt or
  verifier result;
- perform a live read, proposal, confirmation, appointment mutation, signed
  approval, product action, deployment or release;
- store PII, clinical content, prompts, transcripts, credentials, provider
  output, protected evidence or historical Diary material; or
- add product behaviour, durable retry, concurrency, retention, dead-letter
  handling, human-gate UI or autonomous action.

The accepted protocol document and proofreader remain the frozen semantic
source. The rehearsal may orchestrate their declared outcomes but may not
change a verdict, repair rule, authority ceiling, port, frame or lineage.

## 3. Boundary classification and API Spine pattern

Boundary classification:
`repository_local_in_memory_authored_synthetic_control_plane_rehearsal`.

The accepted API Spine remains unchanged:

- input context is typed, minimal, source-labelled and non-authoritative;
- identity, availability, policy and freshness remain supplied synthetic facts;
- the rehearsal can retain candidate, advisory and evidence envelopes only in
  memory;
- a human-gate envelope is confirmation-needed evidence, not approval or a
  command;
- GraphQL remains read-only and unused;
- REST/OpenAPI remains the explicit future command boundary and is unused;
- manifests and scripts are validated declarative inputs, not authority; and
- no `docs/api-spine/` artifact or product source changes.

## 4. Frozen rehearsal decisions

### 4.1 Finite tape, not an autonomous executor

The canonical script is an ordered list of scenarios. Each scenario has a
fixed initial state, no more than 32 authored steps and one declared terminal
state. The whole document has no more than 256 steps. Steps have no `goto`,
branch expression, loop condition, wall-clock delay, random choice, callback,
dynamic import, template expansion or executable string.

The runner may only consume the next step. It cannot discover or synthesize a
next action. Reordering, skipping, repeating or appending a step changes the
source hash and fails deterministic validation or expected evidence.

### 4.2 Frozen step vocabulary

The representable actions are exactly:

- `submit-attempt`;
- `verify-drafts`;
- `apply-verdict-disposition`;
- `record-verified-release`;
- `record-human-gate-delivery`;
- `record-bounded-correction-request`;
- `bind-inert-fresh-read-grant`;
- `supersede-declared-attempt`;
- `reject-stale-completion`;
- `abort-declared-edge`; and
- `finish-scenario`.

Every action records evidence in memory only. None names an endpoint, command,
query, topic, DSN, image, credential, provider or executable capability.

### 4.3 Accepted proofreader reuse

`verify-drafts` calls the accepted pure deterministic proofreader over the
canonical protocol document. The authored step may name only an existing
verification case and its exact declared attempt. The runner compares the
computed verdict, disposition, repair and release envelopes with the step's
expected posture. A mismatch stops the rehearsal with
`revision_required`; the tape cannot override the proofreader.

### 4.4 Attempts, retry and abortion

An attempt can be submitted once per scenario. A correction request may be
recorded only after the proofreader returns `request-new-attempt`. If the tape
then submits a later attempt, it may advance only along existing `retry_of`
lineage. The minimal correction record carries reason codes and coordinates,
never the draft body or hidden reasoning. A scenario may stop with a bounded
correction request and no fabricated successor attempt.

When the accepted retry budget returns `abort-edge`, the runner records an
aborted edge and cannot submit another attempt on that scenario. Authority
rejection also aborts immediately. There is no automatic retry loop.

### 4.5 Fresh-read supersession

The stale-context scenario may bind only the accepted inert fresh-read grant,
whose `execution_enabled` and `returns_data` values remain false. It may then
advance only to the declared later attempt through exact `superseded_from`
lineage, record rejection of the stale generation and finish in
`awaiting-fresh-context`. No fresh read or replacement frame occurs.

### 4.6 Release and human gate

Only proofreader-produced verified edges may enter the in-memory release set.
Atomic groups release all-or-none. A human-gate step may reference only a
verified human-gate edge and records `execution_enabled: false`,
`command_authority: false` and `human_action_performed: false`.

Rejected, stale or aborted frames cannot be routed to a human gate. The runner
cannot rehabilitate them or convert confirmation-needed evidence into approval.

### 4.7 Immutable evidence chain

Each transition record includes sequence, scenario, action, from-state,
to-state, referenced accepted coordinates, previous transition hash and its own
canonical SHA-256. The first record binds the script and protocol source hashes.
The runner never writes that chain; tests compare the returned in-memory result
with the committed expected evidence.

## 5. Canonical rehearsal coverage

The authored tape must cover at least:

1. primary five-port verification, downstream release and inert human routing;
2. both accepted canonical repair verdicts;
3. schema rejection followed by one declared corrected attempt and human route;
4. grounding rejection followed by the declared repeated failure and edge abort;
5. stale-context rejection, inert grant binding, supersession, stale-completion
   rejection and `awaiting-fresh-context` stop;
6. immediate authority-rejection edge abort; and
7. atomic inconsistency with no partial release and a bounded correction
   request only.

The rehearsal proves state-machine conformance over pre-authored outcomes. It
does not prove cognition, interpretation quality, model safety, container
isolation, live authorization, operational scheduling or product behaviour.

## 6. Exact implementation surface

Implementation is limited to:

- `scripts/ariadne_scripted_cognitive_work_cell_rehearsal.py`;
- this plan, the design, threat-model delta and closeout;
- `orchestration/continuity/ariadne-scripted-cognitive-work-cell-rehearsal.schema.json`;
- `orchestration/continuity/ariadne-scripted-cognitive-work-cell-rehearsal-example.json`;
- `orchestration/continuity/ariadne-scripted-cognitive-work-cell-rehearsal-evidence.json`;
- `tests/test_ariadne_scripted_cognitive_work_cell_rehearsal.py`;
- exact receipts, Sol acceptance and one metadata-only node record;
- mechanical Continuity/Compass orientation updates after acceptance; and
- the live handover and orchestration ledger after all gates pass.

No product source, API contract, database fixture, runtime configuration,
frontend, provider artifact or external-worker artifact is in scope.

## 7. Acceptance gates

The tranche passes only when:

1. schema, canonical tape and source hashes validate;
2. the accepted work-cell protocol, verifier, manifests and evidence remain
   unchanged and pass their existing tests;
3. every rehearsal reference resolves to an accepted attempt, draft, case,
   retry trace, grant, released edge or human-gate policy coordinate;
4. all scenarios are forward-only, length-bounded and use only the frozen step
   vocabulary;
5. two rehearsals of the same tape return byte-identical evidence and hash
   chains;
6. no step can override a proofreader verdict or disposition;
7. retry follows exact immutable lineage and cannot exceed the accepted budget;
8. stale context cannot proceed without the inert grant and exact supersession,
   and no fresh data is fabricated;
9. aborted or rejected edges cannot release or reach a human gate;
10. atomic inconsistency releases no partial group member;
11. human-gate delivery is verified, inert and non-command;
12. mutations introducing loops, skips, repeated attempts, undeclared
    references, source-hash drift, dynamic strings, persistence or actuator
    language fail closed;
13. static inspection proves no database, network, product, provider, model,
    subprocess, container, thread, timer, mailbox or command actuator import;
14. the CLI exposes only `validate`, `rehearse` and `trace`, writes no file and
    prints only fixed labels plus aggregate counts;
15. focused and combined Ariadne/API Spine/handover tests, Ruff, compilation,
    JSON parsing and whitespace gates pass serially; and
16. closeout claims remain limited to an in-memory authored-synthetic rehearsal.

## 8. Allocation and reasoning

GPT Sol Extra High owns architecture, implementation, tests, acceptance and
protected integration. No external worker, native subagent or model reviewer is
assigned because the state machine, inherited proofreader contract and
negative-path authority evidence are tightly coupled, and this tranche opens no
model/provider connection. Closeout will claim deterministic local Sol
acceptance, not an independent external veto.

## 9. Deferred decisions

Fresh Yuri authority remains required for adaptive or generated drafts, a fake
or real model, a real container, concurrency, timers, persistent state,
durable queues/retries, live mailbox delivery, product context reads,
PostgreSQL, an event-feed adapter, human-gate UI, signed approval, appointment
command, PII, protected/historical evidence, Stage 3B, production, deployment,
release or autonomous action.
