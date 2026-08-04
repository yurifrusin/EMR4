# Native advisory analysis: model-required Bureau A3 Rayleen rehearsal

Date: 2026-08-04

Role: bounded native read-only/advisory analysis; no acceptance, integration or
authority-expansion right

Source HEAD: `2de467e23ce44574395ad6115e7205ca27c96fb2`

## Rehydration receipt

Decision: `pass`

`rehydrated_from_receipt: true`

The five authoritative sources were restored before this analysis:

1. `live_handover_current_baton`: `AGENTS.md` was read completely. The current
   accepted result is
   `model_required_bureau_c3_d3_provider_free_architecture_pass`; A3/B3 was the
   recommended next material fork.
2. `current_authority_allocation`: `AGENTS.md` section 4 was restored. GPT Sol
   retains architecture, acceptance, recovery and integration authority. This
   native lane owns only this advisory file.
3. `active_plan_and_acceptance`:
   `docs/emr4-model-required-bureau-a3-b3-occupied-rehearsal-plan.md`,
   `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`, the
   accepted provider-free successor design/contract/schema/examples, and the
   C3/D3 and successor closeout/Sol-acceptance records were read. The A3/B3 plan
   freezes the exact Sydney Vertex boundary and no product/read/write boundary.
4. `protected_evidence_boundaries`: `AGENTS.md` sections 5 and 6 and the A3/B3
   plan's closed surfaces were restored. Protected holdouts, patient/clinical/
   product-derived data, historical Diary material, product reads, commands,
   writes, actuators, deployment, release, Pages and protected refs remain
   closed. `docs/branding/` and the preserved Consultant/Gate-minus-one files
   remain excluded.
5. `git_refs_and_worktree`: observed HEAD and local/origin task ref were
   `2de467e23ce44574395ad6115e7205ca27c96fb2`; local/origin `master` and
   `handoff/current` were all
   `2e34bdad732fdab32fbf778280b3d3c70d66d602`. The worktree contained only the
   protected pre-existing untracked material plus Sol-owned A3/B3 plan and
   receipt artifacts before this file was created.

The EMR4 API Steward source pass also covered the mixed API Spine ADR and
programme, Access AI design, Bernie release gates, current prototype manifests
and invariants, and the blueprint-first/model-second boundary.

## Finding

The A3 Rayleen rehearsal is ready to be implemented as one closed Access AI
development-harness invocation, provided the occupied executor uses the exact
provider boundary already frozen by Sol. The smallest robust form is not a
free-text answer and not the general Gate-zero envelope authored by the model.
It is a selector-only model body. The broker must add attempt, cell, context,
label, timestamp and authority fields which the model is not allowed to mint.

This retains the accepted rule:

> the model interprets; the deterministic proofreader grounds and constructs
> the released projection; no candidate field is command or success evidence.

## API Spine classification

- Boundary: `access_ai_external_command_development_harness`.
- GraphQL: unused and read-only; no provider field or mutation.
- REST/OpenAPI: the eventual mounted equivalent would require a separate
  single-purpose Access AI command with actor, practice, capability, method,
  correlation, idempotency, context hash, data class, provider/model/region,
  cost and audit policy. This tranche mounts no route.
- Events: unused and non-authoritative.
- Manifests: declarative provider/cell policy only; typed code enforces it.
- Product/database command plane: absent. No appointment, status, arrival or
  waiting-area command envelope exists in A3.

Suggested stable capability and method names for evidence, not for a mounted
product registry, are `admin.waiting_room.interpret` and
`evaluate_authored_synthetic`.

## Minimal closed Rayleen model body

Use a dedicated Draft 2020-12 schema for the bytes the model authors. Keep the
accepted Gate-zero `TypedCandidate` as the broker-assembled outer envelope.
This avoids trusting the model to echo immutable scope, timestamps, hashes,
labels or cell identity.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://emr4.local/schemas/rayleen-a3-model-candidate.v1.json",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version",
    "intent",
    "projection_kind",
    "target_appointment_ids",
    "evidence_source_ids"
  ],
  "properties": {
    "schema_version": {
      "const": "emr4.rayleen.a3.model_candidate.v1"
    },
    "intent": {
      "enum": [
        "read",
        "explain",
        "filter",
        "group",
        "focus",
        "clarify",
        "check_in_proposal",
        "status_proposal",
        "waiting_area_move_proposal",
        "refuse"
      ]
    },
    "projection_kind": {
      "enum": [
        "current_arrivals",
        "waiting_state",
        "waiting_area_group",
        "practitioner_group",
        "threshold_band",
        "longest_wait",
        "flow_exception",
        "selected_focus"
      ]
    },
    "target_appointment_ids": {
      "type": "array",
      "minItems": 1,
      "maxItems": 8,
      "uniqueItems": true,
      "items": {"type": "string", "format": "uuid"}
    },
    "evidence_source_ids": {
      "type": "array",
      "minItems": 1,
      "maxItems": 16,
      "uniqueItems": true,
      "items": {
        "type": "string",
        "pattern": "^[a-z][a-z0-9_.:-]{2,100}$"
      }
    }
  }
}
```

For this rehearsal, the task policy should further constrain `intent` to
`explain`, `projection_kind` to `longest_wait`, and
`target_appointment_ids` to exactly one item. Keeping the reusable schema's
accepted A2 vocabulary while applying a narrower immutable task policy makes
the policy explicit and avoids changing schema meaning after the call.

The model body deliberately has no prose, patient token, practitioner,
location, waiting-area, elapsed-minute, threshold, authority, confirmation,
command, write, success, timestamp, hash, label, retry or cost field. The
broker assembles the outer candidate with:

- `attempt_id`, `cell_generation_id` and domain `rayleen`;
- candidate kind `waiting_room_projection`;
- practice scope and source-context hash copied from the admitted request;
- broker-observed emission time; and
- per-field labels beginning with integrity `untrusted_model`, reader
  `deterministic_proofreader` and authority ceiling `projection_candidate`.

The released candidate must be a different deterministic object. The
proofreader copies or derives any patient display token, practitioner,
location, waiting area, wait duration, rank and fixed explanatory template from
the accepted frame. It never republishes arbitrary model text.

## One safe authored-synthetic scenario

Scenario id: `rayleen-a3-explain-unique-longest-wait`

Staff utterance:

> Explain who has been waiting longest at North Clinic.

Use a fresh A1 `WaitingRoomContextFrame` with two authored-synthetic arrived
appointments in the same authored-synthetic practice and location:

- Morgan token `synthetic:morgan-lee`, appointment
  `11000000-0000-4000-8000-000000000004`, arrived at `07:50Z`, with a
  deterministically derived elapsed wait of 10 minutes and unique longest-wait
  rank 1 at the frame observation time;
- Casey token `synthetic:casey-wong`, appointment
  `11000000-0000-4000-8000-000000000007`, arrived at `07:56Z`, with a
  deterministically derived elapsed wait of 4 minutes and rank 2;
- both resources and every practitioner/location/waiting-area identifier are
  declared in the frame, and every fact/signal label is fresh and expires at
  the frame's two-minute boundary;
- Morgan's target fact and signals carry source identifiers
  `authored_synthetic_fixture:rayleen-a3.morgan` and
  `authored_synthetic_projection:rayleen-a3.longest-wait`.

The exact expected model body is:

```json
{
  "schema_version": "emr4.rayleen.a3.model_candidate.v1",
  "intent": "explain",
  "projection_kind": "longest_wait",
  "target_appointment_ids": [
    "11000000-0000-4000-8000-000000000004"
  ],
  "evidence_source_ids": [
    "authored_synthetic_fixture:rayleen-a3.morgan",
    "authored_synthetic_projection:rayleen-a3.longest-wait"
  ]
}
```

The proofreader independently recomputes the unique longest-wait target from
arrival timestamps and the caller-supplied evaluation time. It releases a
fixed-template projection such as `rayleen_current_longest_wait_v1`, target
appointment, proofreader-derived display token, elapsed minutes, practitioner,
location and waiting area, plus grounding/context binding. It sets command,
confirmation, proposal, write, database, network, event, provider and
model-to-database authority to literal false. No human action or product
effect follows.

This is a good occupied case because the model must map ordinary language to
the accepted A2 intent/projection vocabulary and select a grounded target, but
deterministic code can independently verify every released value.

## Deterministic proofreader order

Run the checks in a frozen order and release nothing on the first failure:

1. Verify the one-use ledger, attempt/cell generation, frozen provider policy,
   request reservation and task/schema hashes.
2. Parse bounded canonical UTF-8 JSON; reject invalid UTF-8, duplicate keys,
   trailing bytes, non-object output and byte-budget overflow.
3. Validate the exact model-body schema and reject Pydantic/JSON-schema
   coercion, default insertion and unknown properties.
4. Assemble and validate the Gate-zero outer `TypedCandidate` using only
   broker-owned immutable bindings and `untrusted_model` labels.
5. Recompute the `WaitingRoomContextFrame` hash, require exact practice,
   location, context revision and source-context-hash equality, and require the
   caller-supplied evaluation time in `[generated_at, expires_at)` with no
   superseding revision.
6. Enforce the task-specific `explain`/`longest_wait` relationship and one-
   target cardinality. The model cannot broaden to another accepted A2 intent
   merely because the general schema names it.
7. Reject clinical reasoning, confirmation, private Rayleen action, command,
   write, success, free-form execution or authority-shaped material before
   grounding.
8. Resolve every target appointment and every evidence source identifier in
   the exact frame. Require each evidence id to label the target fact or a
   deterministic signal for that same target.
9. Recompute elapsed waits and longest-wait ordering. Require one unique winner,
   the target to equal that winner, status `arrived`, and all referenced
   practitioner/location/waiting-area identifiers to be present and in scope.
10. Construct a new fixed-template released projection from frame truth,
    monotonically join labels, hash grounding/context bindings, validate the
    released schema atomically and only then emit one candidate.

No safe repair should modify the model body or its meaning. Reference sorting
or deduplication is unnecessary because the model-body schema requires unique
arrays and the expected form is canonicalized only for hashing, not silently
rewritten for admission.

## Closed denial vocabulary

At minimum, the A3 result union should carry exact terminal denial codes for:

- parser/envelope: `INVALID_UTF8`, `BYTE_BUDGET_EXCEEDED`, `DUPLICATE_KEY`,
  `TRAILING_BYTES`, `SCHEMA_REJECTED`, `OUTER_ENVELOPE_INVALID`;
- context/scope: `CONTEXT_HASH_MISMATCH`, `CONTEXT_REVISION_MISMATCH`,
  `CONTEXT_STALE`, `CONTEXT_SUPERSEDED`, `PRACTICE_SCOPE_MISMATCH`,
  `LOCATION_SCOPE_MISMATCH`;
- authority/policy: `INTENT_NOT_ALLOWED_FOR_TASK`,
  `PROJECTION_NOT_ALLOWED_FOR_TASK`, `CLINICAL_REASONING_FORBIDDEN`,
  `DIRECT_CONFIRMATION_FORBIDDEN`, `PRIVATE_ACTION_FORBIDDEN`,
  `FREE_FORM_COMMAND_FORBIDDEN`, `WRITE_OR_SUCCESS_CLAIM_FORBIDDEN`,
  `AUTHORITY_CEILING_EXCEEDED`;
- grounding: `APPOINTMENT_UNKNOWN`, `APPOINTMENT_OUT_OF_SCOPE`,
  `APPOINTMENT_STATE_INELIGIBLE`, `EVIDENCE_SOURCE_UNKNOWN`,
  `EVIDENCE_NOT_BOUND_TO_TARGET`, `PROJECTION_RESULT_MISMATCH`,
  `PROJECTION_AMBIGUOUS`;
- broker/lifecycle: `PROVIDER_REQUIRED_UNAVAILABLE`, `BROKER_FAILURE`,
  `CALL_BUDGET_EXCEEDED`, `COST_BUDGET_EXCEEDED`, `FALLBACK_ATTEMPTED`,
  `QUOTA_BREACH`, `RESIDUE_INCOMPLETE`.

All denials carry only sanitized hashes, field paths, source ids already safe
for evidence, failed rules, call count and literal-false release/command/write
fields. Unsupported grounding, scope, freshness, safety, policy, authority,
provider, transport and lifecycle denials are terminal for this tranche.

## One-call correction eligibility

The optional second A3 call is eligible only after an HTTP-successful primary
turn yields a bounded response whose failure is purely response-form contract
conformance. The closed eligibility codes should be:

- `MODEL_BODY_REQUIRED_FIELD_MISSING`;
- `MODEL_BODY_UNKNOWN_PROPERTY`;
- `MODEL_BODY_ENUM_INVALID`; or
- `MODEL_BODY_CARDINALITY_INVALID`.

The correction ticket should contain only version, lane, target turn 2,
original task/context/schema hashes, previous candidate hash, exact eligible
violation codes and field paths, allowed enum/cardinality information,
`replacement_required=true`, `attempts_remaining=1` and an expiry. It must not
contain raw provider bytes, prose, hidden reasoning, a changed utterance,
changed context, new facts or a suggested semantic answer. Turn two is a full
replacement and terminal.

Invalid UTF-8, duplicate keys, trailing bytes, over-budget output, forbidden
authority material, unsupported identifiers, a wrong longest-wait target,
ambiguous projection, stale/superseded context and provider/transport/
credential failures are not correction-eligible. A provider request-schema
admission failure is also terminal: it produced no model candidate and cannot
consume the model-correction path as if the model had made an error. Any
eligible turn-two call still needs a fresh one-use ledger, full pre-call
regating and cost reservation.

## Durable evidence fields

Retain only allowlisted metadata and hashes:

- evidence schema/version, result label
  `occupied_model_authored_synthetic`, source HEAD and plan/policy/schema/
  prompt-template hashes;
- lane `rayleen_a3`, scenario, attempt, cell-generation, ledger and parent-
  dialogue identifiers;
- exact provider, `gemini-2.5-flash`, project, service account identity,
  keyless impersonated-ADC method, OAuth scope, region, regional endpoint and
  API method; never a token or credential material;
- identity/model/region/cache/audit preflight decisions and their sanitized
  evidence hashes;
- request/context/task/model-body hashes, context revision, expiry and
  minimization profile, but no raw prompt, frame or provider response;
- HTTP-success flag/status class, latency, prompt/candidate/total tokens,
  estimated and reserved USD, lane and cumulative call counts, and explicit
  cache/tools/grounding/retrieval/fallback false values;
- parser/schema/proofreader verdict, reason codes, correction eligibility,
  correction-ticket hash, turns used, admitted candidate hash, released
  schema/hash/field allowlist, grounding source ids/digest and fixed template;
- literal candidate-runtime counters for product reads, database access,
  commands, confirmations, writes, actuators, cloud/IAM mutation, deployment,
  release, Pages, protected-ref movement and protected-evidence access;
- pre/post teardown process, listener, mount, token, credential and temporary-
  artifact residue counts, all zero at closure; and
- source-review transport in a separate evidence scope from A3 candidate-
  runtime provider calls.

Evidence must also state `raw_prompt_persisted=false`,
`raw_provider_response_persisted=false`, `product_data_used=false`,
`patient_or_clinical_data_used=false`, `command_envelope_created=false`,
`write_performed=false`, `success_readback_claimed=false` and
`fallback_used=false`.

## Stop and claim boundary

A3 may pass only after at least one HTTP-successful exact-lane provider turn
produces this grounded proofreader-admitted Rayleen projection and complete
cleanup evidence. A schema-correct but ungrounded answer, a provider-blocked or
failed turn, a proofreader rejection or an eligible correction that does not
pass is a truthful terminal A3 result, not a partial pass.

Even a pass proves only one occupied authored-synthetic Rayleen interpretation
and deterministic projection admission. It does not prove live waiting-room
use, patient/product data handling, a mounted Access AI route, Rayleen UI,
arrival/status/waiting-area command authority, product delivery, production or
release.

## Handoff

Recommended Sol implementation: freeze the model-body, released-result,
correction-ticket, ledger and evidence schemas first; implement provider-free
parser/proofreader/ledger/residue negative cases; run exact zero-call preflight
and independent source veto; only then permit the serial occupied A3 call under
the parent A3/B3 cost and call ceilings.

Reasoning level: high advisory analysis over a material provider boundary;
acceptance remains exclusively with GPT Sol.
