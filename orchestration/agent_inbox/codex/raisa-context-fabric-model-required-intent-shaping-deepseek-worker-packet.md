# Context Fabric model-required intent shaping — DeepSeek implementation packet

Source HEAD: `5ddc052fae16298436d8873312e48464d52a9567`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\context-fabric-model-intent-shaping`

Branch: `codex/context-fabric-model-intent-shaping-worker`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No model, transport or implementation fallback is authorised.

## Mandatory rehydration and skills

Before editing, read `AGENTS.md` completely and report the five named sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Read completely:

- `C:\Users\sarashera\.codex\skills\emr4-api-steward\SKILL.md`;
- `docs/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal-plan.md`;
- its design and threat-model delta;
- the accepted provider-free parent plan, design, closeout and implementation;
- `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`;
- `docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-plan.md`;
- `docs/emr4-model-required-bureau-a4-product-read-ui-plan.md`; and
- only the A3/B3 and A4 contract/broker/live modules needed as immutable reuse
  examples.

Verify the exact branch, source HEAD and clean worktree before editing. The
worker has implementation/test ownership only. GPT Sol retains architecture,
acceptance, recovery, integration, provider execution and protected-ref
authority.

## Task

Implement the provider-free contract, schemas, dry-run/occupied controller and
focused tests for the frozen authored-synthetic model-required intent-shaping
rehearsal. Do not make a provider call. Do not create an occupied ledger or
occupied evidence. The code must make later occupied execution possible only
after an exact source-review receipt and read-only preflight.

The implementation path is:

`IntentShapingRequest -> exact Gemini request -> closed ProviderIntentBody -> ModelIntentCandidateEnvelope -> deterministic intent proofreader -> trusted parent IntentRetrievalCandidate -> unchanged parent catalog/binding/retrieval -> unchanged parent same-packet proofreader -> read-context-only release`

The provider receives no parent source catalog, frame contents, binding,
identity or command material.

## Owned files

- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live.py`
- `scripts/raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance.py`
- `tests/test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/intent-shaping-request.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/provider-intent-body.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/model-intent-candidate-envelope.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/cell-request.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/single-use-ledger.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/cost-ledger.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/occupied-rehearsal-evidence.schema.json`
- `orchestration/continuity/raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal/authored-synthetic-intent-shaping-request.json`

Do not edit any other path. In particular, do not edit the frozen plan/design/
threat delta, `AGENTS.md`, `implementation_plan.md`, accepted parent artifacts,
historical A3/B3/A4/C5/Sydney artifacts, `app/**`, `docs/diary/**`,
`docs/branding/**`, API Spine, harness settings, global Continuity/Compass maps,
provider credentials, protected evidence or refs.

The acceptance generator may write provider-free evidence only when GPT Sol
later invokes it with an explicit output path. Do not create or commit generated
provider-free or occupied evidence in the worker commit.

## Exact contract constants

- policy id:
  `raisa-context-fabric-model-required-intent-shaping-sydney-v1`;
- provider/model: Vertex AI `gemini-2.5-flash`;
- project: `bernie-emr4-dev`;
- identity:
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` through existing
  keyless impersonated ADC;
- region/host: `australia-southeast1` /
  `australia-southeast1-aiplatform.googleapis.com`;
- `thinkingBudget: 1024`, `maxOutputTokens: 2048`, temperature 0,
  candidateCount 1, JSON response and no tools/retrieval/cache;
- maximum two calls/USD 0.50 at USD 0.25 reservation per call, no fallback;
- no raw prompt/provider text/response/thought/header/token/credential retention;
- occupied lane id: `rayleen_context_fabric_intent_shaping` only.

The authored-synthetic request text is exactly:

`Compare the current waiting-room operational picture with the earlier state at 10:30 this morning, using only what was known by 12:30.`

It is labelled synthetic, timezone `Australia/Brisbane`, reference date
`2026-08-06`, and maps the only allowlisted coordinate code
`SYNTHETIC_1030_VALID_1230_KNOWN` to parent fixture timestamps
`2026-08-06T00:30:00Z` / `2026-08-06T02:30:00Z` in trusted code only.

Provider output has exactly:

- `intent_code`: one accepted parent intent code;
- `temporal_coordinate_code`: `NONE` or
  `SYNTHETIC_1030_VALID_1230_KNOWN`;
- `cue_codes`: canonical unique array from closed codes
  `CURRENT_STATE_REQUESTED`, `PRIOR_STATE_REQUESTED`, `VALID_TIME_1030`,
  `KNOWLEDGE_CUTOFF_1230`;
- `response_code: INTENT_CANDIDATE_ONLY`; and
- exact false authority fields `identity`, `tenancy`, `patient`, `source`,
  `provider_tool`, `database`, `command`, `write`.

The occupied case proofreader requires
`CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON`, the synthetic coordinate and the
four cue codes in canonical order. It then calls the accepted parent builder
with the template-owned Current+Historical components/profiles and requires the
parent proofreader `RELEASE`. No model field controls requesting Bureau,
component/profile lists, timestamps, limits, binding or source catalog.

Provider-free cases should prove safe wrapping of all five accepted intent
codes through the parent contract using code-owned authored fixtures, plus the
occupied case and wrong/unknown/extra/authority/tamper failures. Do not claim
that the one occupied utterance proves all-language accuracy.

## Broker and live-controller requirements

Reuse the accepted A3/B3 and A4 one-shot transport principles without modifying
their modules or artifacts. New namespaces, schemas, runtime names, attempt ids,
ledgers, source-review path and output paths are mandatory. Later live mode must:

1. reject unless the exact reviewed-source hash map and one fresh source-review
   receipt pass;
2. run the existing read-only exact identity/project/model/region preflight;
3. reserve a single-use ledger before each call;
4. admit exactly one HTTP response, one candidate and one non-thought text part;
5. retain only allowlisted safe response shape/hash/bytes/finish/usage metadata;
6. require positive `thoughtsTokenCount` for occupied acceptance;
7. allow one complete-replacement second call only for
   `provider_body_schema_invalid` or `intent_not_grounded`, with no prior body;
8. consume the ledger after a provider call whether or not release occurs;
9. make no call after admission and never fallback; and
10. close ledger/evidence and prove complete owned runtime cleanup.

The dry-run path must make zero provider calls and emit canonical synthetic
provider metadata/candidate through the same parser, wrapper and proofreaders.
Historical ledgers remain immutable. Later occupied output paths must be absent
before launch and created atomically once.

## Deterministic acceptance

Tests must cover at least:

- all schemas are Draft 2020-12 closed and fixture-valid;
- provider request has exact model allocation, response schema and no forbidden
  data/tool fields;
- request size/response size and one-candidate/one-text-part bounds;
- body schema closure, enum/cue canonicality and all-false authority;
- exact occupied classification and temporal coordinate grounding;
- wrong plausible intent, missing/extra cue, coordinate mismatch, prose/extra
  field, true authority and resealed tamper all block;
- trusted wrapper supplies every parent authority/disclosure field;
- parent catalog/binding and upstream/same-packet proofreader recomputation;
- all five code-owned provider-free intent fixtures traverse the parent engine;
- request/body/candidate/parent/release digest tamper blocks;
- primary/correction eligibility, distinct request hashes, two-call/USD 0.50
  ceilings, zero-call dry-run, no fallback and no post-success call;
- source-review hash binding and missing/wrong/stale receipt failure;
- safe telemetry excludes raw/provider/thought/header/token/credential values;
- AST/static proof of no `app` import, DB/model/requests/httpx/socket/product
  route, command or cloud/IAM mutation in the pure contract/acceptance path; and
- inherited parent, API Spine and plan tests remain unchanged.

Evidence labels are exactly
`provider_free_authored_synthetic_model_intent_shaping` and
`occupied_authored_synthetic_model_intent_shaping`.

## Verification and commit

Do not run repository pytest or PostgreSQL; GPT Sol owns the serial test lease.
You may run Ruff, `py_compile`/`compileall`, JSON Schema validation, direct pure
imports and `git diff --check`. Commit only the owned files using explicit path
staging. Never use `git add .` or `git add -A`. Do not fetch, merge, rebase,
switch, push, call a provider, inspect credentials, run Docker or modify any
cloud/product/runtime state.

Return the five-source statement, exact commit and files, checks, blockers and
finish with exactly one terminal `DECISION: pass` or
`DECISION: revision_required`. A material semantic/authority/provider change
returns immediately to Sol; at most one later mechanical repair is eligible.
