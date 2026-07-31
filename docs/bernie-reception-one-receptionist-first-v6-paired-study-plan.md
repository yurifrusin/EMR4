# Reception One Receptionist-first v6 Paired Development Study

Status: active — provider-blocked gates before occupied execution
Recorded: 2026-07-30

## Authority

Yuri authorised:

- a receptionist-first prompt rather than a form-clerk-first prompt;
- a fixed bounded thinking budget;
- a rerun of the last twenty-four authored-synthetic utterances;
- access to both the natural receptionist response and typed form;
- a running local notebook showing each test input and admitted output; and
- retention of provider-supplied thinking-token counts, but not hidden
  chain-of-thought content.

This is a new descendant of the closed v5 broad-language capability result.
It does not revise or rescore that historical node.

## Question

Can Gemini 2.5 Flash, when briefed first as a medical receptionist and given
the API schema as a pre-printed bureau form in its toolkit, produce:

1. a useful natural receptionist response;
2. a correctly completed typed form; and
3. agreement between those two outputs

more reliably than v5 on the same closed development cohort?

## Paired-development boundary

The exact twenty-four v5 utterance cases are replayed only as a paired
development comparison. They are no longer an independent holdout and no
post-change result may be described as generalisation evidence. A later
evaluation requires a fresh untouched authored-synthetic cohort.

The v5 manifest and frame hashes remain the input anchor. v6 changes:

- the system instruction;
- the response envelope;
- the deterministic response/form agreement gate; and
- `thinkingBudget` from 0 to 1024.

Temperature remains 0. The provider response remains constrained to one exact
JSON envelope, but the prompt describes that envelope as:

- a `receptionist_response` card;
- a short bounded `decision_note`;
- exact evidence-utterance indices; and
- a separate `typed_form` whose `version_code: 3` is broker-owned.

The natural response and form are displayed separately in the running
notebook. The broker never scrapes prose to construct the form.

## Reception desk teaching

The prompt must teach the smallest lessons justified by the closed v5 result:

- understand the whole utterance sequence before filling the form;
- later corrections supersede earlier details;
- exact times must not be broadened into nearby alternatives;
- `call off`, `take out` and `remove` can express cancellation when their
  appointment target is grounded;
- noun-only appointment details do not themselves authorise creation;
- `fit in` without an explicit ordinary-booking or squeeze-in meaning is
  clarification-only under the frozen policy;
- every operator must receive exactly its declared typed sources;
- prior outputs may be referenced only when an earlier operator exposes the
  named output; and
- omission is permitted only for optional inputs.

These are desk instructions and form guidance, not demonstration answers for
the individual cases.

## Output and proofreader contract

The model authors:

- `receptionist_response`: one or two concise reception-desk sentences;
- `decision_note`: one bounded audit sentence beginning with the exact closed
  goal name;
- `evidence_utterance_indices`: one or more valid zero-based indices;
- `typed_form.operator_note`;
- `typed_form.goal_code`; and
- `typed_form.steps`.

The broker injects only `version_code: 3`.

The deterministic gate verifies:

- exact local schema;
- valid evidence indices;
- a bounded, non-command-shaped natural response;
- a bounded decision note matching the typed goal;
- goal-specific vocabulary agreement between the natural response and typed
  form;
- the unchanged typed compiler and semantic proofreader;
- correction eligibility and the one-turn ceiling;
- freshness, supersession and exact cloud binding; and
- atomic release of admitted in-memory typed fields only.

No hidden reasoning, raw provider response or full provider prompt is retained.
The provider-supplied `thoughtsTokenCount`, when present, is retained as an
integer usage measure.

## Running notebook

`orchestration/continuity/reception-one-receptionist-first-v6/running-test-notebook.md`
is rewritten after every closed case. It records:

- case identifier and authored-synthetic utterances;
- schema-admitted natural receptionist response;
- schema-admitted decision note and evidence indices;
- schema-admitted typed form;
- proofreader findings and correction use;
- final in-memory disposition;
- prompt, visible-candidate, thinking and total token counts; and
- the corresponding closed v5 result.

It excludes credentials, tokens, API-key information, raw provider packets,
full prompts and chain-of-thought. A response rejected before local schema
admission is represented only by its bounded failure classification.

## Provider and authority boundary

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- location: `australia-southeast1`;
- endpoint hostname:
  `australia-southeast1-aiplatform.googleapis.com`;
- data: authored-synthetic only;
- isolation: credential-free work cell and one-use host broker;
- maximum: twenty-four primaries plus at most one closed correction per case;
- absolute call ceiling: 48;
- incremental application-cost ceiling: USD 1;
- temperature: 0;
- thinking budget: 1024;
- thought content requested or retained: false;
- API keys, service-account keys, global endpoints and fallback: false;
- tools, function calling, grounding, retrieval and cache creation: false; and
- product/database access, confirmation, writes and delivery: false.

## Deterministic gates

Before an occupied call:

1. five-source rehydration and pre-plan receipts pass;
2. official Vertex request controls are recorded from current Google
   documentation;
3. schema, prompt, notebook and proofreader tests pass;
4. provider-blocked and real-isolation rehearsals pass;
5. relevant API Spine and repository-only Ariadne tests pass;
6. Continuity and Compass advance together and the rendered Compass validates;
7. the existing exact Bernie ADC and cloud-control preflight passes without
   cloud mutation; and
8. independent container, network, image, credential and process residue is
   clear.

Each case stops after its first admitted result or its terminal second turn.
Every ledger is consumed. No mid-cohort prompt, schema, temperature, budget or
proofreader change is permitted.

## Cost bound

At the absolute 48-call ceiling, 3,000 prompt tokens and 2,048
thinking-plus-visible-output tokens per call remain below USD 1 under the
current Gemini 2.5 Flash public list prices. Actual cost is recomputed from
provider usage metadata. Reaching the ceiling without a complete result fails
closed.

## Claim limit

This study can compare v5 and v6 on the same twenty-four authored-synthetic
development inputs through the configured and observed Sydney locational
request path. It cannot prove an independent holdout improvement, exhaustive
language reliability, production fitness, Australian physical or sovereign
processing, or safety for real, product-derived, patient, health, clinical,
protected or historical data.
