# EMR4 model-required Bureau A3/B3 occupied advisory rehearsal plan

Date: 2026-08-04

Status: authorised exact-boundary development rehearsal; no product or write
authority

Source HEAD: `2de467e23ce44574395ad6115e7205ca27c96fb2`

Parent:
`docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`

## Decision and objective

Yuri selected the previously recorded Sydney Vertex development envelope for
the paired A3 Rayleen and B3 Davida authored-synthetic occupied advisory
rehearsal. This plan makes that material boundary exact so the standing
uninterrupted-development authority can carry the tranche through design,
implementation, deterministic admission, independent source review, occupied
execution, bounded recovery, acceptance and task-branch publication.

The objective is narrow: prove that each named intelligent lane includes one
accepted provider-model turn and releases only a closed, grounded,
proofreader-admitted advisory candidate. A3 receives no patient or live
waiting-room data. B3 receives no live practice-administration data. Neither
lane reads from or writes to the product.

## Exact provider and identity boundary

| Property | Frozen value |
|---|---|
| Provider | Google Cloud Vertex AI |
| Model | `gemini-2.5-flash` |
| Project | `bernie-emr4-dev` |
| Service account | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` |
| Authentication | existing keyless impersonated service-account ADC only |
| OAuth scope | `https://www.googleapis.com/auth/cloud-platform` |
| Location | `australia-southeast1` |
| Endpoint | `australia-southeast1-aiplatform.googleapis.com` |
| API path | regional Vertex `generateContent` for the exact model |
| Fallback | none; provider, model, region and global-endpoint fallback blocked |

The existing ADC may be refreshed and inspected read-only. Codex may not
create, replace, reconfigure or persist credentials, modify IAM, enable APIs or
change provider-managed configuration. Exact identity, model catalogue,
prediction-only permission, audit readiness and the existing disabled-cache
posture must pass before a prompt can leave the machine. Failure closes the
attempt before the provider call and identifies any human-only recovery.

## Data, prompt and retention boundary

- Input is newly authored synthetic data bound to repository schemas. It is not
  copied, transformed or inferred from patient, clinical, historical diary,
  product, production, protected or participant material.
- A3 uses a synthetic `WaitingRoomContextFrame` and one synthetic staff
  utterance. B3 uses a synthetic practice-administration context frame and one
  synthetic manager utterance.
- Each prompt contains only its own lane's minimal typed frame, closed output
  contract and task instruction. Cross-lane context and conversational memory
  are absent.
- Raw prompts and raw provider responses are transient inside the one-attempt
  boundary and are not committed, logged or retained. Durable evidence keeps
  hashes, allowlisted provider metadata, usage counts, proofreader decisions
  and admitted typed fields only.
- Provider tools, grounding, URLs, retrieval, code execution, filesystem,
  database, callback and arbitrary network access are absent.
- Provider-managed caching must remain explicitly disabled; no cached-content
  resource is supplied or created.

## Call, retry and cost boundary

- A3 receives one primary call and B3 receives one primary call.
- Each lane may receive at most one second call only when its deterministic
  parser/proofreader emits a closed correction ticket for schema or contract
  conformance. The utterance, context, authority ceiling and task semantics
  cannot change between turns.
- Safety, policy, unsupported-grounding, cross-scope, stale-context, credential,
  entitlement, provider, transport and ambiguous-authority failures are not
  retryable inside this tranche.
- Each lane stops immediately after its first admitted candidate or terminal
  rejection. No unchanged duplicate and no call after admission are allowed.
- Absolute ceilings are two calls per lane, four calls cumulative and USD 1
  cumulative including reservation for every conditionally eligible call.
- A consumed ledger cannot be reused. Every admitted call requires a fresh
  single-use ledger and pre-call cost reservation.

## Isolation and authority structure

Each attempt uses a fresh credential-free, one-task cognitive cell. Only a
short-lived one-use broker may hold the existing impersonated ADC and contact
the exact regional endpoint. The broker admits the canonical request, enforces
size/call/cost policy, strips raw provider material after parsing and passes a
closed candidate to deterministic proofreading. Teardown removes every owned
cell, relay, network, token and temporary artifact; residue evidence must be
clear before and after occupied execution.

The model is a candidate generator only. It cannot mint context facts,
authorization, confirmation, idempotency, audit, command, write, success or
readback evidence. The proofreader may admit a projection/advisory candidate,
issue one closed correction ticket or reject. It cannot repair identity,
resource selection, authority or meaning.

## A3 Rayleen lane

The authored-synthetic frame is practice- and location-scoped, fresh and
minimal. It contains backend-labelled arrival/waiting facts and deterministic
elapsed-wait signals only. The model must emit a closed candidate using the
accepted Rayleen intent grammar and projection kinds. Every referenced
appointment, practitioner, location, waiting area and evidence identifier must
exist in the frame.

The proofreader rejects clinical reasoning, direct confirmation, a private
Rayleen action, scope broadening, invented identity or fact, stale revision,
unsupported explanation, free-form command material and any write/success
claim. Admission releases only a reversible projection/advisory candidate.

## B3 Davida lane

The authored-synthetic frame is restricted to active practitioners, active
locations and an existing deterministic default-location dry-run result. The
model must emit one closed read, explanation, validation, dry-run or proposal
candidate using the accepted Davida grammar.

The proofreader rejects patient/appointment assumptions, inactive or foreign
resources, bulk expansion, negation loss, stale context, delegated
confirmation, administration, invented dry-run evidence, free-form command
material and any apply/write/success claim. Admission releases only an
advisory candidate; the existing deterministic context desk, proofreader and
dry-run contracts remain authoritative and uncalled by the occupied harness.

## API Spine classification

This tranche is an Access AI external command at a repository-local development
harness boundary. It is not GraphQL, a browser provider call or a product
route. Any future mounted invocation must be a separately authorised,
single-purpose REST/OpenAPI Access AI command with actor, scope, correlation,
idempotency, audit, freshness and cost fields. GraphQL remains read-only,
events remain non-authoritative hints and YAML remains declarative.

## Acceptance and execution order

1. Closed Draft 2020-12 schemas, canonical synthetic frames/requests and exact
   provider/authority policy validate deterministically.
2. Negative tests prove cross-scope, invented identifiers, stale context,
   delegated confirmation, write/success claims, retry drift, call overflow,
   cost overflow, fallback and retained raw material fail closed.
3. Provider-free broker/cell dry-runs prove one-use ledgers, proofreader
   admission/correction/rejection, no side effects and complete residue cleanup.
4. The exact ADC/identity/project/model/region/cache/audit/cost preflight passes
   read-only with zero provider calls.
5. A fresh Gemini 3.6 Flash/high source-only veto reviews the exact clean
   candidate after deterministic gates. That review is not A3/B3 product-model
   evidence and uses no patient, clinical or product data.
6. The A3 and B3 primary occupied turns run serially. An eligible correction is
   separately regated and reserved before its one allowed second call.
7. Durable evidence distinguishes candidate-runtime provider calls from
   source-review transport, records exact usage/cost metadata and proves no
   product/database/write/actuator effect and complete cleanup.

The full pass result is
`model_required_bureau_a3_b3_occupied_advisory_rehearsal_pass` only if both
lanes receive at least one HTTP-successful model turn and each releases one
proofreader-admitted grounded candidate. A provider-blocked, provider-failed or
proofreader-rejected lane is recorded truthfully as a bounded terminal result;
no partial result is promoted to end-to-end success.

## Closed surfaces

Patient, clinical, historical diary, protected, participant, product-derived
and production data remain closed. Product reads, mounted routes, UI wiring,
database access, appointment/status/waiting-area/administrative commands,
writes, actuators, shell, SQL, cloud/IAM mutation, update/import/migration,
deployment, production, release, Pages, protected refs and protected evidence
remain closed. `docs/branding/` and the four preserved Consultant/Gate-minus-
one pre-push receipt/state files remain excluded.
