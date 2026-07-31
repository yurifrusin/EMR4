# Reception One Bureau Typed Plan Protocol - Provider-Free Tranche Plan

Date: 2026-07-29

Owner: Yuri / GPT Sol

Status: `approved_scope_frozen_for_provider_free_implementation`

## 1. Authority and objective

Yuri authorised starting the Bureau Typed Plan Protocol after reviewing the
proposed watcher, historical-Diary and typed model/proofreader architecture.
This tranche implements the provider-free foundation needed before an occupied
model may contribute a plan.

The exact objective is:

`reception_one_bureau_typed_plan_protocol_provider_free_pass`

The tranche will prove that the accepted deterministic language engine and one
pre-authored novel composition can produce or simulate untrusted typed plan
drafts, that a deterministic proofreader can admit only safe compositions of a
closed operator catalogue, and that a bounded in-memory executor can run only
the admitted authored-synthetic read/proposal plan.

This authority opens no provider call, credential use, product-data read,
database access, appointment mutation, new API route, event family, historical
Diary processing, production, deployment or release.

## 2. Inherited boundaries

The tranche is a new Continuity descendant of
`reception-one-integrated-bureau`. It does not revise that node or any
historical Ariadne, provider, holdout or product node.

The accepted boundaries remain:

- the model or deterministic planner may emit only an untrusted `PlanDraft`;
- the deterministic proofreader is the only egress gate;
- the executor may perform only declared pure, read or proposal operations;
- no operator may confirm, mutate, call an external provider, open a network
  connection, use credentials or claim a completed action;
- GraphQL remains read-only;
- REST/OpenAPI proposal and confirmation commands remain backend-owned;
- an admitted proposal still requires explicit staff confirmation and backend
  revalidation;
- committed events may invalidate freshness but never grant command authority;
- protected holdouts remain sealed; and
- raw historical Diary material remains local, ignored and outside this
  tranche.

The current interpretation gates remain:

- `runtime_or_provider_wiring_ready=false`;
- `raw_trove_access_ready=false`; and
- `runtime_gate_decision=blocked`.

Those values do not prevent this repository-only provider-free protocol. They
do prevent treating it as provider/runtime/trove readiness.

## 3. API Spine classification

Boundary classification:

`provider_free_typed_agent_plan_contract_and_in_memory_proposal_dry_run`.

The accepted API Spine pattern is:

- typed minimal context frames supply the complete authored-synthetic evidence
  universe;
- a planner selects only declared operator identifiers and typed dataflow
  bindings;
- read operators correspond to bounded context reads;
- proposal operators correspond to existing proposal command families;
- no plan contains a provider URL, database query, REST path, bearer token,
  credential, raw command payload or confirmation operation;
- the proofreader verifies practice/correlation/context binding, schema,
  operator signature, dataflow type, grounding, freshness, effect ceiling,
  step/revision budgets and acyclic order; and
- the executor returns proposal candidates and evidence only.

## 4. Frozen operator language

The provider-free catalogue may contain only:

- `resolve_patient_reference`;
- `resolve_practitioner_reference`;
- `resolve_date_expression`;
- `read_selected_appointment`;
- `read_patient_appointment_timeline`;
- `read_practitioner_schedule`;
- `search_available_slots`;
- `assess_squeeze_in_options`;
- `prepare_create_proposal`;
- `prepare_move_proposal`;
- `prepare_resize_proposal`;
- `prepare_cancel_proposal`;
- `prepare_status_proposal`; and
- `request_clarification`.

Each operator declares exact input names and types, output names and types,
effect class, corresponding API Spine operation where applicable, and whether
human confirmation is required.

Operator effects are limited to:

- `pure`;
- `authorised_read`; and
- `proposal_only`.

There is no `write`, `confirm`, `provider`, `network`, `database`, `tool`,
`shell` or arbitrary-code effect.

## 5. Plan and review protocol

One `PlanDraft` contains:

- contract and catalogue versions;
- request, practice, correlation and context-revision bindings;
- attempt number and revision ceiling;
- an allowlisted goal and `proposal_only` effect ceiling;
- at most twelve ordered steps;
- exact argument bindings from deterministic semantic fields, supplied context
  fields or earlier typed step outputs; and
- no raw provider reasoning.

The proofreader returns exactly one of:

- `admit`;
- `revision_required`;
- `clarification_required`; or
- `reject`.

Violations contain only allowlisted paths and reason codes. Safe repair is
restricted to whitespace trimming, canonical identifier casing and
deterministic ordering where order is explicitly non-semantic. It cannot
invent a step, reference, value, policy, availability fact, appointment
identity or authority.

A schema/mechanical defect may receive at most one later immutable revision.
Semantic ambiguity routes to `clarification_required`. Unknown operators,
forged context, stale context, cyclic/forward dataflow, effect escalation,
confirmation/write requests and exhausted revision budgets reject.

## 6. Provider-free evidence cases

The authored-synthetic evidence must cover:

1. create appointment;
2. move appointment;
3. resize appointment;
4. cancel appointment;
5. status proposal;
6. a novel squeeze-in assessment composed from existing typed primitives;
7. a mechanical first-draft defect followed by one admitted revision;
8. unknown operator rejection;
9. fabricated or ungrounded reference rejection;
10. forward/cyclic dataflow rejection;
11. stale-context rejection;
12. write/confirmation escalation rejection; and
13. revision-budget exhaustion.

Known action plans must be derived from the existing deterministic
`extract_semantics()` output rather than a second natural-language parser. The
novel squeeze-in case may use a pre-authored untrusted plan, but every value it
uses must still resolve from the deterministic semantic frame, supplied
context or an earlier typed output.

## 7. Bounded executor

The executor is an in-memory authored-synthetic proof only. It:

- accepts only a proofreader result with `disposition=admit`;
- checks the exact reviewed plan hash and context revision again;
- runs operators in the reviewed topological order;
- sources all facts from the supplied synthetic input frame;
- returns bounded typed outputs and a trace of operator identifiers;
- may prepare a proposal candidate naming the existing API Spine operation ID;
- always records `write_performed=false`,
  `confirmation_performed=false`, `provider_calls=0`,
  `network_access=false`, `database_access=false` and
  `product_delivery=false`; and
- cannot execute a REST command or reuse its result as confirmation evidence.

## 8. Watcher and supersession seam

The plan input carries a context revision. A later committed-event watcher may
increment that revision after a relevant event and fresh read. The proofreader
and executor reject the earlier plan as stale. This tranche simulates that
revision mismatch only; it does not add or alter an event producer, poller,
outbox, SSE relay or browser behaviour.

## 9. Exact implementation surface

The tranche is limited to:

- this plan, a design record, threat-model delta and closeout;
- `scripts/reception_one_bureau_typed_plan_protocol.py`;
- JSON Schemas, catalogue, authored-synthetic cases and deterministic evidence
  under
  `orchestration/continuity/reception-one-bureau-typed-plan-protocol/`;
- `tests/test_reception_one_bureau_typed_plan_protocol.py`;
- additive rehydration, pre-plan and pre-acceptance receipts;
- a new Continuity descendant and matching Compass revision after the
  deterministic gates pass;
- the rendered Compass report, live handover and orchestration ledger after
  acceptance.

Existing product, API, provider and historical-evidence files must remain
unchanged except for the final additive current-state bindings named above.
Every unrelated worktree change is preserved.

## 10. Acceptance gates

The tranche passes only when:

1. all schemas validate under Draft 2020-12;
2. catalogue and cases validate exactly and reject unknown properties;
3. the deterministic engine supplies known-action semantic fields;
4. all admitted plans are acyclic, type-correct, grounded, fresh and
   proposal-only;
5. the squeeze-in case demonstrates a novel safe composition without a new
   primitive or overbooking authority;
6. typed plan/review dialogue is bounded to one revision;
7. no rejected draft reaches execution;
8. every executor fact is a subset or deterministic transformation of supplied
   authored-synthetic context;
9. create, move, resize, cancel and status results name only existing proposal
   operation IDs and require human confirmation;
10. static inspection proves no provider, credential, network, database,
    subprocess, shell, command-confirmation or product-delivery actuator;
11. focused protocol, deterministic language, API Spine, Bounded Cognitive
    Work Cell, Continuity and Compass tests pass serially;
12. JSON validation, Python compilation, Ruff and `git diff --check` pass for
    the scoped files;
13. Continuity and Compass increment together and the rendered report validates
    before any later occupied provider call; and
14. closeout claims remain provider-free and authored-synthetic.

## 11. Live Vertex stop boundary

No occupied provider call is authorised by this plan. The prior Sydney
rehearsal authority and ledgers are consumed.

Before a model-connected product-text lane, Yuri must freshly name the exact
provider, model, project, service account, authentication class, region,
endpoint, isolation, proofreader, external audit, cost ceiling, call ceiling,
data class and stop boundaries. The future lane may not be inferred from
reference coordinates in an older artifact.

## 12. Allocation

GPT Sol owns this tightly coupled protocol implementation, tests and
acceptance. No external worker, subagent or provider is selected. No commit,
push, pull request or protected-ref movement is authorised in the current
dirty shared worktree.
