# Reception One Bureau Typed Plan Protocol

Date: 2026-07-29

Status: provider-free authored-synthetic implementation

## Purpose

The protocol gives Reception One a language in which an adaptive planner may
compose a novel request without receiving command authority. The planner
chooses from a closed catalogue of typed operations; the deterministic
proofreader validates the plan; a bounded executor may then run only the
admitted authored-synthetic read/proposal composition.

This implementation is deliberately provider-free. The same `PlanDraft`
contract can later become the egress format of an isolated cognitive work cell,
but it is not connected to one here.

## Relationship to the Bureau

The accepted Bureau separates three desks:

- the typewriter emits an untrusted typed draft;
- the proofreader admits or rejects exact fields; and
- the typesetter projects only admitted results over fresh Diary truth.

This protocol deepens the first two desks. A `PlanDraft` is more expressive
than the earlier single intent draft: it is a bounded directed sequence of
typed operators. It still cannot reach the typesetter or a command unless the
proofreader admits the complete plan.

## Coarse cognition, fine authority

The planner may reason across one coherent receptionist request and combine
several safe primitives. Authority remains fine-grained:

- resolution operators produce synthetic patient or practitioner references;
- read operators consume typed references and supplied context;
- proposal operators produce candidates for staff review;
- no operator confirms or writes;
- no operator invents an API path, database query, provider call or tool; and
- a capability absent from the catalogue is rejected rather than improvised.

Novelty therefore means a new composition of known safe primitives, not a new
primitive or authority.

## Typed bindings

Every operator argument is one of four bindings:

1. `semantic_ref` — a value already produced by the existing deterministic
   `extract_semantics()` boundary;
2. `utterance_ref` — an exact source span that must resolve to one supplied
   patient, practitioner or status value;
3. `context_ref` — one exact allowlisted context object, currently the selected
   appointment or squeeze-in policy; or
4. `step_output` — a typed output from an earlier admitted step.

There are no free-form literal IDs, SQL fragments, endpoints, commands or
provider messages. A step output may refer only backwards. This makes the plan
an ordered acyclic dataflow graph without requiring an executable programming
language.

## Operator catalogue

The catalogue has fourteen operators and three effect classes:

- `pure`;
- `authorised_read`; and
- `proposal_only`.

The proposal operators name the relevant API Spine `operationId` for later
adapter work:

| Typed operator | API Spine reference | Runtime effect here |
|---|---|---|
| `search_available_slots` | `proposeSlotSearch` | synthetic in-memory read |
| `prepare_create_proposal` | `proposeAppointmentCreate` | candidate only |
| `prepare_move_proposal` | `proposeAppointmentUpdate` | candidate only |
| `prepare_resize_proposal` | `proposeAppointmentUpdate` | candidate only |
| `prepare_cancel_proposal` | `proposeAppointmentDelete` | candidate only |
| `prepare_status_proposal` | `proposeAppointmentStatus` | candidate only |

The reference does not execute the operation. Confirmation operation IDs are
absent from the catalogue.

`assess_squeeze_in_options` is intentionally advisory. It consumes a supplied
policy that forbids moving existing appointments and overbooking, returns only
pre-supplied `squeeze_in_review` candidates, and requires staff review. It has
no API operation ID because no squeeze-in command has been authorised.

## Deterministic proofreader

The proofreader normalises only mechanical identifier whitespace and casing,
then checks in fixed order:

1. exact Draft 2020-12 schema;
2. request, practice and correlation binding;
3. context revision and expiry;
4. authored-synthetic data class;
5. catalogue version;
6. twelve-step ceiling and unique step IDs;
7. known operators;
8. backward-only dataflow;
9. exact operator argument signatures;
10. binding type compatibility;
11. source/context grounding;
12. effect ceiling and forbidden-surface exclusion;
13. deterministic action consistency for known-action plans; and
14. the closed authority envelope.

The output is a typed `PlanReview`:

- `admit`;
- `revision_required`;
- `clarification_required`; or
- `reject`.

Diagnostics contain only an allowlisted JSON-style path and reason code. They
do not contain a rejected payload or hidden reasoning.

## Typed dialogue and retry

One mechanical plan defect may return `revision_required`. The evidence removes
one required `duration_minutes` binding from a valid create plan. Attempt one
cannot execute; attempt two restores the typed binding, receives a new plan
hash and is admitted.

The revision ceiling is two attempts. The same defect at attempt two receives
`revision_budget_exhausted` and rejects. Unknown operators, fabricated
references, forward dataflow, stale context and effect escalation reject
immediately. A missing semantic value that reflects genuine ambiguity routes
to `clarification_required`.

## Bounded executor

The executor accepts only:

- `disposition=admit`;
- `execution_authorized=true`;
- the exact reviewed plan hash; and
- the same context revision.

It resolves all facts from the authored-synthetic frame, runs the fourteen
known implementations through a fixed dispatcher and emits one typed
`final_output`. It cannot dynamically import, evaluate code, construct an HTTP
request, open a database session or dispatch a shell command.

Every result records:

- `write_performed=false`;
- `confirmation_performed=false`;
- `provider_calls=0`;
- `network_access=false`;
- `database_access=false`; and
- `product_delivery=false`.

Proposal results name a family, API Spine reference, synthetic entity
references, candidate slots, warnings and the human-confirmation requirement.
They are not signed evidence and cannot be submitted as confirmation.

## Evidence cases

The existing deterministic semantic engine supplies the known-action plans:

- create;
- move;
- resize;
- cancel; and
- status change.

The novel squeeze-in utterance is not classified as a complete known action by
the deterministic engine. A pre-authored untrusted plan composes patient and
practitioner resolution, date resolution, a practitioner schedule read and the
bounded squeeze-in assessment. The proofreader admits it because every binding
is grounded and every operator is known; this is the precise freedom intended
for a future model.

Negative evidence proves rejection of:

- an unknown database-shaped operator;
- a fabricated patient mention;
- a forward reference;
- a stale context revision;
- a confirmed-write effect; and
- a mechanical defect after the revision budget is exhausted.

No rejected case reaches the executor.

## Watcher seam

The watcher remains outside the cognitive lane. Its future role is to advance
the authoritative context revision after a relevant committed event and fresh
read. A plan returning with the previous revision receives `stale_context` and
cannot execute.

This tranche proves the comparison only. It does not change the current
committed-event table, polling interval, endpoint, client reconciliation or
opened event family.

## API Spine and Access AI result

Boundary classification:

`provider_free_typed_agent_plan_contract_and_in_memory_proposal_dry_run`.

GraphQL remains read-only and unused. REST/OpenAPI commands remain the future
proposal/confirmation boundary and are not invoked. No provider adapter is
loaded. If a model later inhabits the planner, Access AI and the accepted
isolated broker/work-cell boundary must mediate it; the browser must never call
a provider directly.

## Unproved surfaces

This protocol does not prove live model interpretation, product context reads,
authorization against a real user or practice, FastAPI routing, PostgreSQL,
event-driven invalidation, API proposal execution, signed confirmation,
appointment mutation, real data, receptionist usability, production,
deployment or release.
