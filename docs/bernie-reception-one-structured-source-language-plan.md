# Reception One Structured Source Language Plan

## Decision and objective

Yuri authorised a new continuity descendant of the closed Reception One Shared
Typed Language result. The historical arithmetic-source programs, consumed
ledgers, failed proofreader dispositions and call ceiling remain immutable.

The objective is to test whether Gemini can fill out the same bounded planning
form more reliably when a prior result is represented as explicit typed
coordinates rather than a hand-calculated composite integer. The model remains
free to interpret novel receptionist language, choose and order operators, wire
their typed properties together, and provide one independently bounded
`operator_note`. It gains no command or scheduling authority.

## PlanProgram v3

`reception.one.bureau.plan-program.v3` retains:

- one integer `goal_code` from the frozen seven-goal table;
- an ordered list of integer `operator_code` values from the frozen
  fourteen-operator catalogue; and
- the separately proofread, audit-only `operator_note`.

Each operator argument is now represented by a fixed-shape `source_ref`:

```json
{
  "kind": "prior_output",
  "binding_code": -1,
  "prior_step_index": 3,
  "prior_output_name": "candidates"
}
```

The only source kinds are:

- `binding`: `binding_code` selects one request-local grounded binding;
- `prior_output`: `prior_step_index` selects an earlier step and
  `prior_output_name` selects one frozen output property exposed by that
  step's operator; and
- `omit`: represents an omitted optional input.

All four fields are always present. Unused integer coordinates must be `-1`,
and the unused output name must be `none`. Output names are a closed enum
derived from the accepted operator catalogue; they are not free-form
identifiers.

This removes arithmetic decoding from model work. It does not let the provider
schema decide semantic validity. The deterministic compiler must still verify
the kind/sentinel combination, operator arity, backward-only reference, exact
property existence, semantic type, required inputs, goal/terminal agreement,
grounding, freshness, supersession and proposal-only effect ceiling. It then
mechanically constructs the already accepted PlanDraft and invokes the
unchanged semantic proofreader and in-memory proposal executor.

No natural-language parsing occurs after provider egress. No semantic safe
repair is permitted.

## Bounded operator note

The existing note contract is unchanged. The note is at most 320 UTF-8 bytes,
one line, independently screened, audit-only and never parsed into the program,
executed, product-delivered or used to repair a rejected plan. It must describe
only proposal/review or clarification status and include `no booking was
changed`.

A rejected note is discarded; only its hash and closed reason codes may be
retained. An admitted note may be retained verbatim in the external audit
alongside the schema-admitted typed program. Raw prompts, raw provider
responses and hidden reasoning remain excluded.

## API Spine and authority

This descendant is an internal, default-off, authored-synthetic,
proposal-only provider adapter. It adds no GraphQL mutation, REST route, REST
write, event family, database access or frontend provider call.

The model may prepare only the existing create, move, resize,
cancellation-review, status-change, squeeze-in-assessment and clarification
families. Backend-owned identity, practice scope, appointment truth,
availability, conflicts, confirmation, writes, idempotency and audit remain
authoritative. The final proposal remains human-gated and in memory.

No real, product-derived, patient, health, clinical, protected or historical
data is admitted. Appointment confirmation/write, product delivery, Word
wiring, voice, representative-staff activity, production, deployment, release,
commit, push and protected-ref movement remain closed.

## Conditional Sydney Vertex rehearsal

Only after repository-only, provider-blocked, real-isolation, Continuity,
Compass, rendered-Compass and exact read-only ADC/control gates pass may this
descendant make one primary call and, if eligible, one deterministic
request-contract repair through exactly:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- location: `australia-southeast1`;
- endpoint hostname:
  `australia-southeast1-aiplatform.googleapis.com`.

The incremental application ceiling is USD 1 and the absolute occupied-call
ceiling is two. Stop after the first proofreader-admitted result.

The broker alone may refresh the already configured impersonated ADC and call
the exact regional endpoint. The occupied cell receives no ADC, OAuth
credential, cloud configuration, service-account key or provider API key.
Provider tools, function calling, grounding, retrieval, explicit cache
creation, global endpoints and automatic regional fallback are disabled.

The read-only preflight must freshly verify the exact credential type, project,
target identity, cloud-platform scope, prediction-only role and
`aiplatform.endpoints.predict` permission, Vertex API and billing entitlement,
model entitlement, Vertex Data Access audit logging, disabled or absent
request-response logging, disabled project cache, no service-account key and
no API-key authentication.

No provider, model, project, identity, credential, region, endpoint,
data-class, isolation, proofreader, audit, cost or residency substitution is
allowed. The evidence may establish the configured and observed Sydney
locational request path; it must not claim Australian physical or sovereign
processing.

## Retry rule

A second actual call is eligible only if the first failure is solely a
deterministic request-contract defect. Before that call:

1. consume and independently audit the first ledger;
2. retain only the bounded provider-error contract when applicable;
3. identify the exact mechanical defect;
4. add a focused regression;
5. rerun every repository-only, provider-blocked, isolation, Continuity,
   Compass, rendered-report and exact read-only ADC/control gate; and
6. create a distinct single-use ledger.

A semantic plan, dependency, grounding, note or proofreader failure is not
repairable and ends the occupied sequence. No model-selected source may be
silently changed.

## Deterministic acceptance

Provider-free acceptance requires:

1. exact JSON and provider-schema validation;
2. lossless PlanProgram-v3 to accepted PlanDraft compilation for every
   supported goal;
3. explicit rejection of invalid source-kind/sentinel combinations, missing
   bindings, forward references, nonexistent output properties, type
   mismatches, unsafe notes and free-form identifiers;
4. focused, inherited typed-plan, relevant API Spine, Continuity and Compass
   tests;
5. Python compilation/static checks, JavaScript syntax checks where relevant,
   repository-only Ariadne verification and `git diff --check`;
6. a credential-free real-isolation lifecycle with single-use exchange,
   deterministic teardown and independent residue checks; and
7. revision-bound Continuity/Compass and a valid rendered Compass report before
   any occupied call.

Occupied acceptance additionally requires HTTP 200, exact PlanProgram-v3 and
note admission, unchanged semantic proofreader admission, atomic release of
only typed authored-synthetic proposal fields, a consumed ledger, valid
external hash chain and complete cleanup.

A failure remains a valid fail-closed result only when no draft is released,
no unauthorised retry or fallback occurs, every ledger is consumed, cleanup is
complete and the handover states the unresolved gate candidly.
