# Reception One Proofreader Dialogue v4 Plan

## Decision and lineage

Yuri authorised a new v4 descendant by saying, `Ok let's start v4.` The
provider-free Structured Source Language v3 result remains immutable: its
explicit source-reference form, twenty focused tests, real-isolation evidence
and zero-provider-call status are inherited evidence, not revised history.

V4 is the bounded dialogue protocol around the unchanged
`reception.one.bureau.plan-program.v3` form. It does not rename or broaden the
fourteen-operator language.

## Objective

Test whether an LLM planning clerk can:

1. interpret one authored-synthetic receptionist request;
2. fill the explicit typed PlanProgram form;
3. understand one deterministic typed rejection; and
4. submit one complete corrected form that the independent proofreader can
   safely admit.

The production question is not whether the model is infallible. It is whether
useful first- or second-turn form completion can coexist with fail-closed
proofreading and zero unverified release.

## Dialogue contract

The dialogue protocol is
`reception.one.bureau.proofreader-dialogue.v4`. Each provider turn receives:

- the complete unchanged authored-synthetic v3 task form;
- `turn_code`, either `1` or `2`; and
- either no correction ticket or one exact
  `reception.one.bureau.proofreader-correction-ticket.v1`.

The response on both turns is the unchanged PlanProgram-v3 schema. Turn two is
a complete replacement, never a patch.

The correction ticket contains only:

- a version code and target turn;
- the hash of the complete rejected PlanProgram;
- the rejected typed form with `operator_note` removed;
- one to twenty allowlisted findings;
- for each finding, a closed violation code, closed field code, bounded step
  and source indexes, and a closed list of output names allowed by the
  referenced earlier operator when applicable; and
- `attempts_remaining: 1`.

It contains no rejected note text, raw provider response, raw prompt, hidden
reasoning, credentials, person identifiers, product data or free-form
proofreader message.

The existing independently screened `operator_note` remains audit-only. An
admitted note may be recorded beside the typed form. A rejected note is not
placed in the ticket; only the complete-program hash and allowlisted finding
survive.

## Proofreader authority

The proofreader may report that a field violates a frozen constraint. It may
publish the closed output names actually exposed by an already selected earlier
operator. It must not choose the goal, operator, dependency, binding, slot,
patient, practitioner, time or proposal for the model.

No semantic safe repair is added. Mechanical normalisations already admitted
by the accepted proofreader remain local and explicit. Every corrected
selection must be authored by the model in the complete second form and pass
the full proofreader independently.

Correction-eligible first-turn findings are limited to:

- exact source-reference sentinel, arity, backward-reference, output-name,
  binding and semantic-type defects;
- closed PlanDraft signature, duplicate, binding-type, grounding,
  clarification and semantic-action findings that do not indicate an opened
  authority, data, freshness or scope boundary; and
- the existing closed operator-note finding codes.

No correction ticket is issued for stale context, non-synthetic data, scope or
catalogue mismatch, effect escalation, forbidden operator, authority-boundary
failure, credential or sensitive-data concern, provider transport failure, or
a response that cannot be reduced to the exact local PlanProgram schema.

Turn two is terminal. Admission releases only the existing authored-synthetic
proposal fields. Rejection, clarification, malformed output or provider failure
edge-aborts or routes to the inert human gate. There is no third turn.

## Call-budget state machine

The absolute occupied ceiling remains two actual provider calls and USD 1:

- if turn one is admitted, stop;
- if turn one is schema-admitted and correction-eligible, turn two may carry
  the typed correction ticket;
- if turn one fails solely because of a deterministic provider request-contract
  defect, the second call may be used only after the existing closed-ledger,
  independent-audit, focused-regression and complete-gate-rerun procedure; and
- the correction turn and request-contract repair compete for the same second
  call. Neither can open a third.

Each actual call has a distinct one-use child ledger. A parent dialogue audit
binds the two turn identifiers, ticket hash, provider-call ordinal, proofreader
decisions, release or terminal failure, and both durable hash chains.

## API Spine boundary

This is an internal default-off authored-synthetic `admin_proposal` provider
adapter. It adds no GraphQL mutation, REST route, REST write, event family,
database access, frontend provider call, appointment confirmation or command
actuator.

The model remains an untrusted form filler. The deterministic compiler and
proofreader own admission. Backend identity, practice scope, appointment truth,
availability, conflicts, confirmation, idempotency, writes and product audit
remain authoritative. Any admitted output remains an in-memory, human-gated
proposal with `write_performed: false`.

## Exact occupied lane

Only after every provider-free, isolation, repository, API Spine, Continuity,
Compass, rendered-report and read-only cloud-control gate passes may v4 use:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- location: `australia-southeast1`;
- hostname: `australia-southeast1-aiplatform.googleapis.com`.

The broker alone may use or refresh the existing impersonated ADC. The work
cell receives no ADC, OAuth credential, cloud configuration, provider key or
service-account key. API-key authentication, tools, function calling,
grounding, retrieval, explicit cache creation, global endpoints, automatic
regional fallback and all other providers or regions are prohibited.

The preflight must freshly prove the exact credential, project, target,
cloud-platform scope, prediction-only role and permission, API/billing/model
entitlement, Vertex Data Access logging, disabled or absent request-response
logging, disabled project cache, no user-managed service-account key and no
API-key path.

Evidence may establish only Google's published regional support and the
configured and observed Sydney locational request path. It must not claim
Australian physical or sovereign processing.

## Deterministic acceptance

Provider-free acceptance requires:

1. exact schemas for turn input, correction ticket and inherited PlanProgram;
2. deterministic first-rejection/ticket/complete-replacement/admission proof;
3. rejection of ticket tampering, free-form feedback, unallowlisted findings,
   rejected-note retention, third turns and budget reuse;
4. broker and external-audit proof for admitted first turn, corrected second
   turn, repeated failure and request-contract competition;
5. real credential-free non-root, read-only, bounded, network-isolated
   two-turn fixture execution with complete task residue cleanup;
6. focused, inherited plan/runtime, API Spine, Continuity and Compass tests;
7. JSON/schema validation, Python compilation, static checks, relevant
   JavaScript syntax, repository-only Ariadne verification and
   `git diff --check`; and
8. revision-bound Continuity/Compass plus the exact rendered Compass report
   before any occupied call.

Occupied success requires a consumed ledger for each opened turn, at most two
actual calls, valid per-turn and parent hash chains, unchanged exact cloud
binding, proofreader admission, atomic proposal-only release, no call after
success and complete cleanup.

An occupied failure is an acceptable fail-closed result only if no unverified
form is released, no unauthorised turn or fallback occurs, every ledger is
consumed, cleanup is complete and the handover states the unresolved gate
candidly.

## Closed

Real, product-derived, patient, health, clinical, protected and historical
Diary data; product/database context; appointment confirmation or mutation;
GraphQL mutations; REST route or write changes; Word; voice; representative
sessions; production; deployment; release; commit; push and protected-ref
movement remain closed.
