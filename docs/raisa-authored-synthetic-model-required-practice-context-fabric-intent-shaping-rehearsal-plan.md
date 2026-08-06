# Authored-synthetic model-required Practice Context Fabric intent-shaping rehearsal plan

Date: 2026-08-06

Status: frozen bounded implementation and occupied-execution plan

Parent result:
`raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal_pass`

Parent reviewed source:
`b24b56bda296f3713b5e2c0e52545c749e71540a`

Planning source HEAD:
`8b1f2c8452f4bf03868beae057d7a24cc893fc43`

## Objective

Prove one complete model-required but deterministic-authority intent-shaping
loop over the accepted Context Fabric retrieval contract. An isolated provider
cell receives one newly authored patient-free synthetic staff utterance and a
closed intent vocabulary. It may emit only one closed, non-authoritative intent
candidate body. Trusted code wraps that body, deterministically grounds it,
constructs the accepted `IntentRetrievalCandidate`, and submits the complete
parent retrieval packet to the already accepted same-packet proofreader.

The exact target result is
`raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal_pass`.

The model is mandatory for the occupied intelligent result. It never receives
source records, decides authority, assembles context, retrieves data, executes a
command or declares success.

## Exact authored-synthetic task

The occupied case is a deliberately bounded comparison request:

> Compare the current waiting-room operational picture with the earlier state
> at 10:30 this morning, using only what was known by 12:30.

The request is labelled synthetic, uses `Australia/Brisbane` and synthetic
reference date `2026-08-06`, and contains no person, patient, practitioner,
practice, location or product identifier. The closed temporal coordinate code
`SYNTHETIC_1030_VALID_1230_KNOWN` maps only in trusted code to parent fixture
coordinates `valid_at=2026-08-06T00:30:00Z` and
`known_at=2026-08-06T02:30:00Z`.

The provider sees:

- the exact synthetic utterance and its synthetic/timezone labels;
- the five accepted intent codes with short code-owned descriptions;
- the one allowlisted temporal coordinate code;
- the closed provider-body schema and an all-false authority ceiling; and
- no source catalog, frame content, binding, identity, credential, route,
  database object, command, tool or prior candidate.

## Closed provider output

The provider body contains exactly:

- one of the five accepted `intent_code` values;
- `temporal_coordinate_code`, either `NONE` or the single allowlisted synthetic
  coordinate;
- one or more closed `cue_codes` selected from the request vocabulary;
- constant `response_code: INTENT_CANDIDATE_ONLY`; and
- exact all-false identity, tenancy, patient, source, provider-tool, database,
  command and write authority fields.

It contains no prose, free-text reason, source selector, identifier, timestamp,
SQL, vector query, URL, tool call or command argument. Trusted code supplies the
candidate id, requesting Bureau, issued-at time, template components and field
profiles, temporal timestamps, disclosure maxima, seals and provenance.

## Exact provider, reasoning and accounting boundary

| Property | Frozen value |
|---|---|
| Provider/model | Google Vertex AI `gemini-2.5-flash` |
| Project | `bernie-emr4-dev` |
| Identity | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` through the existing keyless impersonated ADC |
| Region/host | `australia-southeast1` / `australia-southeast1-aiplatform.googleapis.com` |
| Endpoint | `v1/projects/bernie-emr4-dev/locations/australia-southeast1/publishers/google/models/gemini-2.5-flash:generateContent` |
| Data | newly authored patient-free synthetic utterance and closed ontology only |
| Reasoning/output | `thinkingBudget: 1024`; `maxOutputTokens: 2048`; temperature 0; one candidate |
| Calls | at most two cumulative; stop after the first admitted release |
| Cost reservation ceiling | USD 0.50 cumulative at USD 0.25 per call |
| Fallback | none |
| Tools, retrieval and cache | none |
| Raw retention | no raw prompt, provider text/response, thought content, headers, bearer token or credential |

The read-only preflight must verify the exact identity, project, model, region,
endpoint and request hash before an occupied cell opens. Codex receives no
credential, IAM, quota, billing or cloud-configuration mutation authority.

Every attempt uses a new single-use ledger and isolated one-shot cell. A setup,
preflight or transport failure proven to have made zero candidate-runtime calls
may be repaired and rerun only under a new immutable attempt record. A provider
call consumes its ledger reservation even when no candidate is released.

## Deterministic lifecycle

1. Validate the exact backend-authored `IntentShapingRequest` and provider
   request hash before any provider action.
2. Admit exactly one HTTP response, one candidate and one non-thought text part;
   preserve only allowlisted shape, hash, byte, finish and usage metadata.
3. Parse a JSON object and validate the closed provider-body schema.
4. Ground the intent, temporal coordinate and cue codes against the exact
   synthetic request and code-owned expected classification. Any mismatch
   releases nothing.
5. Build the complete accepted parent `IntentRetrievalCandidate` in trusted
   code. The model cannot set Bureau, component, profile, timestamp, maxima,
   identity or authority fields.
6. Recompute the accepted source catalog and backend authority binding, build
   the parent intent packet, and require its proofreader decision `RELEASE`.
7. Release one immutable model-shaped intent-retrieval envelope only when both
   the model-candidate proofreader and parent same-packet proofreader pass.
8. Seal the exact model request hash, sanitized response metadata, candidate
   digest, parent packet digest, proofreader digests, ledger and cleanup result.

No context frame is sent to the provider. No retrieval or source read precedes
model admission in this rehearsal. The model selects only the closed intent;
the deterministic parent contract alone selects context.

## Bounded correction and stop rule

One second call is eligible only after the first call reaches a JSON object and
fails with either `provider_body_schema_invalid` or `intent_not_grounded`.
The correction is a separately hashed complete-replacement request. It contains
the same synthetic utterance and closed ontology plus the safe reason code; it
does not contain the previous provider body and cannot change the provider,
model, region, identity, data, budget, output cap, authority, schema, parent
binding, proofreader or cost ceiling.

No correction follows provider safety refusal, content absence, non-text or
multi-part output, arbitrary transport ambiguity, parent proofreader failure,
positive-thinking evidence failure, exhausted ledger or admission. No call
follows success. Bounded-option exhaustion produces a truthful terminal result,
not a weakened contract or silent fallback.

## Implementation artifacts

- this plan, one design and one threat-model delta;
- a pure closed intent-shaping contract/proofreader module;
- a broker and isolated live/dry-run controller reusing the accepted one-use
  Sydney Vertex transport boundary without modifying its historical artifacts;
- closed request, provider-body, candidate-envelope, ledger and evidence schemas;
- authored-synthetic fixture and provider-free canonical evidence;
- focused tests, acceptance generator, exact-source independent-review packet;
  and later occupied evidence, closeout and continuity artifacts.

No `app/**`, `docs/diary/**`, mounted API, GraphQL root, REST/OpenAPI command,
ordinary service or product-runtime import is added.

## Acceptance

Provider-free acceptance must prove:

1. exact schema closure and rejection of extra/free-text/authority fields;
2. all five closed intents can be wrapped and sent through the unchanged parent
   retrieval contract, while unknown and ambiguous classifications fail closed;
3. the occupied comparison utterance deterministically requires
   `CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON`, the one coordinate code and exact
   cue set; a plausible wrong intent or wrong coordinate releases nothing;
4. model output cannot select Bureau, source component, field profile, source
   fact, identity, disclosure maximum or command authority;
5. the parent catalog, binding and all upstream plus same-packet proofreaders
   are recomputed after model-candidate admission;
6. candidate, request, context, response and proofreader tamper are detected;
7. primary/correction ledgers, USD 0.50 ceiling, no-fallback, no-post-success-call
   and immutable historical namespaces hold;
8. zero provider calls in dry-run and zero filesystem/network/database/
   subprocess/product/API/command/deployment/protected actions in the pure
   contract path; and
9. API Spine regressions prove no read or command surface was opened.

Before an occupied call, the exact clean candidate must pass all deterministic
gates and one fresh Gemini 3.6 Flash/high read-only source veto. Occupied
acceptance additionally requires:

- exact read-only ADC preflight;
- one or, only if eligible, two consumed single-use calls within USD 0.50;
- the frozen 1,024/2,048 request allocation and positive provider-reported
  thinking-token use;
- one deterministically admitted model-shaped parent retrieval packet;
- no raw provider or credential retention, no fallback and no post-admission
  call; and
- complete absence of owned runtime resources after closeout.

Evidence labels are
`provider_free_authored_synthetic_model_intent_shaping` and
`occupied_authored_synthetic_model_intent_shaping`.

## Claim boundary

Passing proves one authored-synthetic closed-intent model path through the
accepted deterministic retrieval contract. It does not prove general
natural-language understanding, real staff language, patient or product privacy,
live source retrieval, a database watcher, persistence/retention, clinical
reasoning, real cross-Bureau handoff, product runtime performance or command
safety. Configured and observed Sydney request routing is not a claim of
Australian physical or sovereign processing.

Patient, clinical, product-derived, financial, protected and historical-PHI
data; real practice/user/source identifiers; raw audit; external evidence/RAG;
live database/session/feed/watcher; persistence/retention; API/runtime wiring;
clinical, prescribing, referral, billing or administrative commands; cloud/IAM
mutation; deployment, production, release, Pages, protected evidence and
protected-ref movement remain closed. Preserve and exclude `docs/branding/`
and all unrelated untracked receipt/state/evidence/cost-ledger files. Git
staging is explicit-path only.
