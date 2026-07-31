# Reception One default-off dual-planner runtime plan

Status: authorised implementation descendant
Recorded: 2026-07-30
Predecessor: `reception-one-readonly-synthetic-diary-context-occupied-result`

## Objective

Connect the already accepted frozen v6.8 isolated model lane to the existing
authenticated Reception One product-context proposal route without weakening
its deterministic baseline or appointment authority boundary.

The route will:

1. remain disabled by default and development-only;
2. continue to require an exact authored-synthetic practice allowlist;
3. default to the existing deterministic planner;
4. accept only the closed planner selector `deterministic` or
   `isolated_vertex`;
5. require a separate default-off gate before `isolated_vertex`;
6. let the trusted backend alone construct the practice-scoped frame and keep
   the raw identifier map;
7. pass the frame to the frozen v6.8 cell through its purpose-built one-use
   broker and exact Sydney Vertex lane;
8. bind proofreading freshness to the backend-observed request wall clock;
9. expose only the proofreader-admitted typed release to the proposal adapter;
   and
10. make both planners return the same proposal-only response contract.

## API Spine classification

This is an authenticated command-style read that prepares a proposal. It is
not GraphQL, an appointment mutation, a confirmation command, an async command
tunnel or a frontend provider call.

Required response invariants:

- `requires_confirmation=true`;
- `proposal_only=true`;
- `write_performed=false`;
- `confirmation_performed=false`;
- `model_database_access=false`;
- exact planner mode and bounded provider-call count;
- typed proofreader disposition, admitted operator identifiers and violation
  paths; and
- one opaque runtime audit reference for an isolated-provider attempt.

## Exact model boundary

- provider: Google Vertex AI;
- model: `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- target service account:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- authentication: existing keyless impersonated service-account ADC;
- location: `australia-southeast1`;
- endpoint:
  `australia-southeast1-aiplatform.googleapis.com`;
- authored-synthetic data only;
- no API key, static key, global endpoint, provider/region fallback, tools,
  grounding, retrieval or cache creation;
- at most one primary plus one proofreader correction per request;
- cost ceiling USD 1 for the occupied acceptance request.

The occupied work cell receives no ADC, OAuth token, API key, Google CLI
configuration, database credential, raw database UUID, handle map or product
network path. The host broker alone may refresh the existing impersonated ADC
and call the allowlisted regional endpoint.

## Freshness design

The trusted backend captures one timezone-aware `observed_at` at the start of
the route. That value binds the frame, desk context, model packet and final
proofreader evaluation. The v6.8 proofreader must use the desk-context
`captured_at` value, verify it matches the frame, and pass it explicitly to the
underlying typed-plan freshness gate. Existing frozen evidence remains
deterministic because its captured time is unchanged.

## Provider-free acceptance

- deterministic mode remains the default and makes zero provider calls;
- requesting `isolated_vertex` while its separate gate is false fails closed
  before a ledger, broker, cell or provider call;
- non-dev, non-allowlisted or non-synthetic requests fail closed;
- planner selection cannot change provider, model, project, identity, region
  or endpoint;
- the model adapter consumes only a proofreader-admitted release;
- model failure or no-release has no deterministic or provider fallback;
- both modes produce the same response type and use the same proposal adapters;
- wall-clock freshness accepts a current frame and rejects an expired or
  mismatched frame;
- no path confirms or writes an appointment;
- focused API Spine, route, schema, isolation and residue tests pass.

## Occupied acceptance

After Continuity, Compass and rendered Compass bind the provider-free result
and a fresh read-only cloud preflight passes, exercise exactly one
authenticated, allowlisted, disposable authored-synthetic route request in
`isolated_vertex` mode. One correction is permitted only if issued by the
frozen proofreader. Every ledger must be consumed; database truth must remain
unchanged; and all owned containers, networks, images, processes and disposable
database state must be removed.

## Historical readiness gate

The generic interpretation harness remains globally closed and unchanged. Run
and record:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

The required generic values remain:

- `runtime_or_provider_wiring_ready=false`;
- `raw_trove_access_ready=false`;
- `runtime_gate_decision=blocked`;
- `default_provider=disabled`;
- `live_provider_enabled=false`;
- `provider_calls_performed=false`;
- `route_behavior_changed=false`;
- `database_access_performed=false`;
- `memory_or_rag_access_performed=false`; and
- `historical_diary_material_access_performed=false`.

This plan does not alter that generic provider boundary. It implements only
Yuri's separately authorised, exact, default-off synthetic route exception.

## Closed gates

Real or product-derived patient or health data, historical Diary material,
appointment confirmation or mutation, model-to-database access, frontend
provider access, Word, voice, representative sessions, production, deployment,
release, provider/model/project/identity/region substitution and stronger
physical or sovereign locality claims remain closed.
