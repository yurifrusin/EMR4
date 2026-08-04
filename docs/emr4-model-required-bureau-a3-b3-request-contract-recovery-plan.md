# EMR4 model-required Bureau A3/B3 request-contract recovery plan

Date: 2026-08-04

Status: authorised bounded recovery descendant; no product, patient-data,
write, deployment, release or protected-ref authority

Source HEAD: `9782c14740ad52cc8ddea6c9fd372b5aaabbcab2`

Parents:

- `docs/emr4-model-required-bureau-a3-b3-occupied-rehearsal-plan.md`
- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `docs/ariadne-autonomous-continuation.md`

## Decision and objective

Yuri authorised a new descendant after the terminal Rayleen A3
`provider_content_invalid` result and directed uninterrupted evidence-backed
diagnosis until an admitted Rayleen/Davida result or exhaustion of materially
distinct bounded remedies. When an in-scope choice exists, the Conductor is to
prefer the bounded path that strengthens occupied Rayleen/Davida capability
without returning for a routine permission formality. This preference cannot
expand any frozen material boundary.

The first recovery changes one coupled generation-allocation policy: Gemini 2.5
Flash receives an explicit `thinkingBudget: 1024` and enough bounded visible-
answer headroom through `maxOutputTokens: 2048`. The prompt, response schema,
temperature, candidate count,
provider, model, project, identity, region, endpoint, data class, proofreader,
isolation, audit, no-fallback posture and authority ceiling remain unchanged.

The old request, response evidence, attempt identifiers and consumed ledgers
remain immutable. Recovery uses a new policy id, attempt/ledger identifiers,
runtime names, artefact root and parent cost ledger.

## Evidence basis and uncertainty

Observed facts:

- the old request omitted `thinkingConfig` and limited total output to 512
  tokens;
- exactly one provider candidate reached the old parser, but its
  `content.parts` was absent, non-list, empty or not exactly one part;
- the old evidence did not preserve enough sanitized metadata to distinguish
  those shapes, the finish reason or token allocation;
- the later Bernie Reception One line used `thinkingBudget: 1024`, retained
  hidden-thought exclusion, and ultimately passed both a 24/24 development
  cohort and an untouched 12/12 authored-synthetic holdout with non-zero
  provider-reported thinking tokens;
- Google documents automatic thinking for Gemini 2.5 Flash when no budget is
  set and documents fixed budgets as the way to constrain it; and
- Google documents structured JSON response schemas as supported for this
  model.

The inference is therefore deliberately limited: unbounded automatic thinking
competing with a small total-output allowance is the strongest current
hypothesis, not a proven retrospective cause. Yuri's architectural preference
is to preserve model reasoning rather than use thinking-off as the default, so
the recovery adopts the already evidenced Bernie 1,024/2,048 envelope. Official
references are:

- `https://cloud.google.com/vertex-ai/generative-ai/docs/thinking`
- `https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output`
- `https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash`
- `https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse`
- `https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/Content`

## Exact provider and accounting boundary

| Property | Frozen value |
|---|---|
| Provider/model | Vertex AI `gemini-2.5-flash` |
| Project | `bernie-emr4-dev` |
| Identity | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` through the existing keyless impersonated ADC |
| Region/host | `australia-southeast1` / `australia-southeast1-aiplatform.googleapis.com` |
| Data | newly authored synthetic A3/B3 frames only |
| Recovery policy | `emr4-model-required-bureau-a3-b3-sydney-recovery-v1` |
| Calls | at most two per lane, four cumulative |
| Cost reservation ceiling | USD 1 cumulative at USD 0.25 per call |
| Fallback | none |

Every opened attempt ledger is single-use. Rayleen runs first. Davida remains
closed unless Rayleen reaches deterministic proofreading and releases one
admitted candidate. No call follows a lane's admitted result. No unchanged
request may be retried.

If the bounded-thinking request fails, sanitized evidence selects at most one next
Rayleen remedy inside the same outer boundary:

1. observed `MAX_TOKENS` may justify a separately hashed output cap of 3,072
   while retaining the 1,024-token thinking budget;
2. an otherwise valid `STOP` response with multiple parts may justify a
   separately reviewed strict part-admission change; or
3. an observed provider `InvalidArgument` may justify a separately reviewed
   schema simplification.

The next remedy changes one causal variable where possible. Removing structured
output, relaxing grounding/proofreading, changing provider/model/region,
introducing fallback, increasing the USD 1 ceiling or adding product data is
not a recovery option. Exhaustion occurs when both calls for a lane are
consumed, the shared ceilings are reached, or no materially distinct remedy
remains inside this plan.

## Diagnostic and release controls

Before candidate extraction, durable evidence records only allowlisted facts:
HTTP status, response byte count/hash, observed model version, candidate count,
finish reason, prompt block reason, content presence, bounded part count/kinds,
text byte count and prompt/candidate/thought/total token counts. Raw prompt,
context, provider text, thought content, finish message, headers, tokens and
credentials are never retained.

Missing content, invalid/empty/multiple parts, thought/non-text parts,
malformed JSON and schema-invalid JSON remain distinct fail-closed outcomes.
The first recovery does not concatenate parts or weaken the one-text-part
admission rule.

The model remains an untrusted selector generator. Deterministic code owns
context, revision, identifiers, grounding, authority, proofreading and atomic
advisory release. Admission is neither confirmation, command, write, effect nor
success.

## Acceptance and execution order

1. Freeze this plan, its threat-model delta, diagnosis evidence, distinct
   schemas/policy/ids and exact bounded-reasoning request contract.
2. Prove the new request hash, unchanged prompt/schema, exact 1,024/2,048
   allocation, strict
   response-shape handling, safe telemetry, ledger ceilings, Rayleen-before-
   Davida gating and historical namespace immutability with provider-free
   tests.
3. Run the isolated provider-free A3/B3 rehearsal and preserve its zero-call
   evidence.
4. Commit the exact clean candidate to the non-protected task branch.
5. Obtain a fresh exact-HEAD Gemini 3.6 Flash/high independent source veto;
   this source-review transport is distinct from candidate-runtime evidence.
6. Run the existing read-only identity/project/model/region/cache/audit
   preflight and then the new Rayleen primary.
7. Start Davida only after Rayleen admission. Apply the same thinking-off
   request contract and deterministic proofreader boundary.
8. Stop only at both-lane admission, bounded-option exhaustion or a genuine
   out-of-scope/user-only fork. Record and publish every attempt truthfully.

The target result is
`model_required_bureau_a3_b3_request_contract_recovery_pass`. A partial or
terminal result cannot be promoted.

## Closed surfaces

Patient, clinical, historical Diary, participant, protected, product-derived
and production data; product/API/UI runtime wiring; product or database reads;
commands, confirmations, writes and actuators; provider tools, retrieval and
arbitrary network; cloud/IAM/credential mutation; update/import/migration;
deployment, production, release, Pages and protected-ref movement remain
closed. `docs/branding/` and the existing Consultant/Gate-minus-one pre-push
receipt/state files remain preserved and excluded. Staging is explicit-path
only.
