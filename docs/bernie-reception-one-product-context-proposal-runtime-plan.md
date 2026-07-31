# Reception One Product-Context Proposal Runtime Plan

Date: 2026-07-29

Owner: Yuri / GPT Sol

Status: `authorised_frozen`

## 1. Authority and objective

Yuri authorised continued necessary tranche work without routine pauses so that
Reception One can progress from an isolated model-text proof into a running
runtime. This plan interprets that authority narrowly.

The objective is a default-off development runtime in which:

1. an authenticated backend constructs a minimal, practice-scoped typed context;
2. an untrusted planner composes only the accepted closed operator language;
3. the deterministic proofreader admits or rejects the complete plan;
4. backend-owned read/proposal adapters resolve fresh truth; and
5. Reception One receives only admitted, proposal-only typed fields.

The backend continues to own identity, availability, conflicts, freshness,
confirmation, writes, idempotency, audit and receipts. No model output is a
command, signed evidence or database value.

## 2. Boundary classification

API Spine classification:

`authenticated_default_off_command_style_read_and_proposal_runtime`.

- GraphQL remains read-only and is not used as a provider or mutation tunnel.
- Existing REST/OpenAPI proposal services remain the only product adapters.
- Existing confirmation commands are outside this plan.
- The model/planner receives typed handles and a minimal frame, never a database
  session, ORM object, bearer credential, provider credential or route client.
- The typesetter receives only proofreader-admitted output plus fresh
  backend-owned read results.

This plan opens repository-local code and tests for a default-off authenticated
proposal runtime. It does not open appointment mutation, production,
deployment or release.

## 3. Legacy gate posture

The legacy Bernie Interpretation Harness gate remains unchanged:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`

The current provider-boundary report remains:

- `default_provider=disabled`
- `runtime_or_provider_wiring_ready=false`
- `live_provider_enabled=false`
- `provider_calls_performed=false`
- `route_behavior_changed=false`
- `database_access_performed=false`
- `memory_or_rag_access_performed=false`
- `historical_diary_material_access_performed=false`

This descendant uses a separate policy and feature flag. It must not set
`docs/bernie-interpretation-harness-runtime-gate.json` to allowed, enable the
legacy interpreter provider, or make `assert_bernie_provider_allowed_by_runtime_gate`
less strict.

Required readiness commands:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

## 4. Frozen product-context contract

The backend may construct only these frame classes:

- authenticated principal: opaque staff, practice and surface bindings;
- request: bounded receptionist utterance, explicit reference date and
  correlation identifier;
- patient candidates: opaque handles and minimal display labels required for
  staff disambiguation;
- practitioner candidates: opaque handles, display labels and active state;
- selected Diary context: opaque appointment handle and exact current revision
  only when the staff surface supplied it;
- availability context: fresh candidate-slot handles, date, local time,
  duration, practitioner handle and warning codes;
- policy context: closed proposal-only effect ceiling, staff-confirmation
  requirement, expiry and data classification.

The frame must be practice-scoped, role-checked, source-labelled, size-bounded,
freshness-bound and default-deny. Free notes, clinical data, appointment reason
text, contact details, date of birth, Medicare details, raw audit rows, broad
Diary history, hidden identifiers, credentials and policy documents are
excluded.

The initial product adapter may read only deliberately authored-synthetic data
inside a disposable local development fixture. Real, product-derived, patient,
health, clinical and historical data remain closed.

## 5. Runtime roles

### Context desk

Trusted backend code authenticates the staff principal, enforces practice
scope, performs the minimum reads and replaces database identifiers with
request-scoped opaque handles before constructing the planner frame.

### Typewriter

The planner is injected behind a closed interface. The default implementation
is provider-blocked. Deterministic and fake-planner implementations are allowed
for routine tests. A live planner can be exercised only by the occupied gate in
section 8.

### Proofreader

The accepted exact-schema, catalogue, scope, grounding, topology, type,
freshness, effect-ceiling and authority checks remain unchanged. Mechanical
repair remains limited to explicit whitespace, canonical enum casing and
deterministic ordering. Rejected drafts never reach adapters or the UI.

### Product adapter

The adapter maps only admitted read/proposal operators to named backend
functions. It cannot construct arbitrary HTTP, SQL, import, shell or provider
calls. It independently checks the reviewed plan hash, context revision,
practice scope and effect ceiling.

### Typesetter

The Bureau renders only a typed proposal envelope. It must state that nothing
is booked and that staff selection/confirmation is required. It receives no raw
prompt, raw response, rejected draft or model reasoning.

## 6. Tranches and deterministic gates

### Tranche A — authority, policy and revision binding

- preserve the completed model-text node and all consumed ledgers;
- add this plan, a separate runtime policy and threat-model delta;
- create five-source rehydration and pre-plan receipts;
- increment Continuity and Compass together;
- validate revision binding and the rendered Compass report.

### Tranche B — provider-blocked runtime kernel

- define exact request, trusted context, planner-draft, review and released
  proposal schemas;
- add a closed planner interface and provider-blocked default;
- adapt the accepted proofreader without weakening checks;
- prove no database, network, provider, credential or product delivery occurs.

### Tranche C — authenticated product-context adapter

- add a separate default-off development feature gate;
- require the existing authenticated appointment roles;
- enforce practice scope before reads;
- build opaque request-scoped handles;
- read only disposable authored-synthetic local fixture data;
- execute only admitted read/proposal operators;
- perform no confirmation, appointment write, event-family expansion or audit
  mutation.

### Tranche D — Bureau proposal delivery

- connect the compact/expanded Bureau request action to the new endpoint only
  when the feature gate is explicitly enabled in the disposable harness;
- retain the ordinary Diary as authority and spatial anchor;
- render typed clarification, candidate and proposal-only states;
- route all future confirmation through the existing separately gated command
  path; this tranche supplies no confirm control capable of writing;
- preserve close, Return, Escape, focus restoration and ordinary fallback.

### Tranche E — live-local provider-free proof

- use a disposable PostgreSQL-backed authored-synthetic practice;
- drive the real local browser, FastAPI and database without route interception;
- prove authentication, practice isolation, fresh reads, proposal-only result,
  zero appointment/audit mutation and deterministic cleanup;
- label this evidence `live_local_browser_backend_postgres_provider_free`.

### Tranche F — bounded occupied authored-synthetic gate

This gate may run only after A-E pass. It may send only the authored-synthetic
fixture utterance and typed authored-synthetic frame; no product-derived,
patient, health, clinical or historical data may be transmitted.

The exact lane is:

- provider: Google Cloud Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- identity:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: `keyless_impersonated_service_account_adc`;
- region: `australia-southeast1`;
- endpoint: `australia-southeast1-aiplatform.googleapis.com`;
- isolation: credential-free work cell plus one-use broker;
- proofreader: the frozen deterministic typed-plan gate;
- fallback: none;
- provider tools, grounding, retrieval and caching: none;
- cumulative application cost ceiling: USD 1.

Each occupied attempt requires a distinct consumed ledger, bounded audit,
cleanup and focused diagnosis before another attempt. Yuri has authorised
necessary same-lane repairs and retries until the first complete admitted
runtime result or bounded-option exhaustion. The sequence stops immediately
after the first admitted result. No provider, model, project, identity, region,
credential, data-class, isolation, proofreader, authority or residency change
is permitted.

### Tranche G — external audit and closeout

- record request/schema/plan/review/release hashes and safe event metadata;
- exclude credentials, raw prompts, raw responses and reasoning;
- consume all ledgers and prove zero provider calls after success;
- remove owned containers, networks, images, processes and temporary roots;
- update Continuity, Compass, rendered report, handover and programme ledger;
- state exactly what the evidence does and does not prove.

## 7. Acceptance requirements

The tranche passes only when:

- every request is authenticated, role-checked and practice-scoped;
- the context is minimal, typed, source-labelled, freshness-bound and
  size-bounded;
- opaque handles cannot be forged across request, practice or revision;
- unknown or stale handles, unknown operators, free literals, effect
  escalation and command-shaped output fail closed;
- no rejected draft reaches a product adapter or typesetter;
- proposal adapters independently revalidate current truth;
- the released envelope is exact, proposal-only and requires staff
  confirmation;
- provider-blocked, fake-planner and adversarial suites pass;
- live-local evidence uses only disposable authored-synthetic data;
- appointment and appointment-audit row counts are unchanged;
- the legacy interpreter gate and default provider remain blocked/disabled;
- provider use, if reached, satisfies the exact occupied gate;
- cleanup and residue checks pass; and
- repository, API Spine, schema, Continuity, Compass, Python, JavaScript and
  whitespace checks pass.

The blocking ordinary receptionist prompt remains:

`Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45`

The novel squeeze-in composition remains an additional required case.

## 8. Stop conditions

Stop for Yuri only if work requires:

- real, product-derived, patient, health, clinical or historical data;
- a production or externally shared environment;
- an appointment confirmation or write;
- a GraphQL mutation or model-to-database write;
- a new IAM, billing, API, credential, provider, model, project, identity,
  region or residency decision;
- weakening the legacy Bernie runtime/provider gate;
- provider fallback, API-key or static-key authentication;
- more than the cumulative USD 1 ceiling;
- credential exposure or a failure to preserve isolation/audit;
- a material user-visible authority or confirmation-policy decision; or
- commit, push, pull request or protected-ref movement while the current
  no-Git-mutation instruction remains active.

## 9. Claim limit

Even a complete pass will prove only a bounded development runtime over
authored-synthetic data, deterministic typed admission and the configured and
observed Sydney locational request path if the occupied gate runs. It will not
prove Australian physical or sovereign processing, real-data safety,
representative receptionist value, production fitness, appointment mutation,
deployment or release.
