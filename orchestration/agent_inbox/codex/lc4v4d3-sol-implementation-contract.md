# LC4V4D3 Sol Implementation Contract — Option A Policy Resolution

Date: 2026-07-15

Authority: Yuri approved Option A in
`docs/bernie-lc4v4d3-option-a-decision.md`. GPT Sol owns architecture,
acceptance, recovery, taxonomy, and protected integration. One DeepSeek V4
Flash/high lane through Claude Code `--bare` is the bounded implementation/test
worker. A fresh Gemini 3.5 Flash project is the independent veto reviewer.
DeepSeek Pro is not authorized.

## Objective

Implement a versioned, deterministic Option A policy-resolution layer over the
exact 20 LC4V4D2 policy-gap cases without changing the already accepted
utterance action/entity/temporal parse or rewriting historical evidence.

Source baseline:

- approved decision baseline and aligned refs:
  `9b468066480bfc79f8df820dba10024d2772e5fe`;
- D2 report hash:
  `sha256:3220ac943659ae1449c5c285144b1fa980f659668a705ca7aef98f0aea6d317a`;
- exact current 20-case policy selection hash:
  `sha256:d3c6618cb586f5dc43824ec7a6e9e33957fee587a45c19f89e5a4bb425006e2a`.

## Exact target population

Clarification alternatives:

- `lc4v4d1_entity_patient_ambiguous_03`
- `lc4v4d1_entity_practitioner_ambiguous_09`
- `lc4v4d1_entity_location_ambiguous_15`
- `lc4v4d1_entity_appt_type_ambiguous_21`
- `lc4v4d1_entity_duration_ambiguous_27`

Corrected patient resolution:

- `lc4v4d1_entity_patient_corrected_04`
- `lc4v4d1_dialogue_correction_single_03`

Practitioner resolution / omitted-practitioner policy:

- `lc4v4d1_entity_practitioner_omitted_08`
- `lc4v4d1_entity_practitioner_corrected_10`
- `lc4v4d1_dialogue_correction_multi_04`

Diary state joins:

- `lc4v4d1_entity_patient_mismatched_06`
- `lc4v4d1_entity_practitioner_mismatched_12`
- `lc4v4d1_entity_location_mismatched_18`
- `lc4v4d1_entity_appt_type_mismatched_24`
- `lc4v4d1_entity_duration_mismatched_30`

Unsafe confirmation bypass:

- `lc4v4d1_safety_create_unsafe_02`
- `lc4v4d1_safety_move_unsafe_04`
- `lc4v4d1_safety_resize_unsafe_06`
- `lc4v4d1_safety_cancel_unsafe_08`
- `lc4v4d1_safety_status_unsafe_10`

## Required architecture

Add a distinct, versioned policy-resolution boundary after pure utterance
extraction and before replay/scoring. The legacy D1/D2 path must remain
reproducible; Option A must be selected explicitly by the D3 evaluator/tests.
Do not make scenario IDs, expected fields, scorer results, or diary-state labels
inputs to utterance parsing.

The policy result must expose enough typed evidence to distinguish:

- final clarification requirement and lossless surfaced choices;
- selected policy tool sequence and authority;
- final resolved patient/practitioner identity where required by replay;
- a separate diary relation such as no conflict, exact duplicate, or field
  conflict; and
- the exact conflicting diary fields without rewriting utterance
  `entity_semantics`.

The policy layer may consume dialogue text, the already-produced semantic
extraction, and the synthetic initial diary state. It must not consume expected
tools, expected choices, expected deltas, scorer failures, scenario IDs, or
protected evidence.

## Required behavior

1. Explicit `A or B` alternatives return only the surfaced alternatives in
   source order, with lossless text and no invented roster options.
2. A corrected patient is searched using the final identity before slot/proposal
   work.
3. A corrected practitioner maps the final surfaced practitioner, including a
   correction turn that does not repeat `with`.
4. Omitted practitioner under create becomes clarification-required with no
   appointment/audit delta and no implicit/default practitioner.
5. Each of the five diary comparisons keeps the utterance target entity
   `exact`, emits a separate field-conflict relation naming only the differing
   field, prevents mutation, and requires state-conflict clarification.
6. Explicit `Bypass confirmation` demands select only `refuse_instruction`,
   emit no appointment/audit delta, and preserve the already accepted base
   action/temporal/entity parse.
7. The versioned Option A path must remain deterministic over two complete
   observations per valid case.

## Evidence

Add a fail-closed D3 evaluator/report that:

- validates the D2 report hash and exact 20-case population/hash;
- records legacy-before and Option-A-after policy results for all 20 cases;
- records the six versioned contract changes rather than treating them as
  historical D1 repairs;
- proves all 20 satisfy the approved D3 contract;
- proves pure utterance entity/action/temporal fields are unchanged from D2;
- proves no mutation for omitted-practitioner, state-conflict, or unsafe cases;
- runs twice and compares complete normalized observations;
- hashes the complete canonical D3 report; and
- never authorizes protected evidence, providers, product runtime, or write
  authority.

## Acceptance

D3 is acceptable only if:

- 20/20 approved Option A cases pass with zero variance;
- all five choice lists exactly match their surfaced alternatives;
- both corrected-patient cases search the final identity;
- both corrected-practitioner cases map Dr Chen to the established synthetic
  `pr-004` identity;
- omitted practitioner clarifies and produces no mutation;
- all five state joins preserve exact utterance semantics, expose only the
  expected differing field, clarify, and produce no mutation;
- all five unsafe cases use refusal-only policy and produce no mutation;
- the frozen D1/D2 reports and hashes remain byte-for-byte unchanged;
- existing D2 semantic, ordinary semantic-extraction, handover, and adjacent
  deterministic tests pass serially; and
- Gemini returns `DECISION: pass` on the exact recovered D3 report head.

## Owned paths

- new `app/services/bernie/lc4v4d3_policy_resolution.py`;
- narrow optional-version wiring in
  `app/services/bernie/composed_corpus_evaluator.py`;
- only if structurally necessary, additive fields/helpers in
  `app/services/bernie/semantic_extraction.py` or
  `app/services/bernie/composed_evaluator.py`, without changing accepted D2
  action/entity/temporal values;
- new `app/services/bernie/lc4v4d3_policy_evidence.py`;
- new `tests/test_bernie_lc4v4d3_policy_resolution.py`;
- new `docs/bernie-lc4v4d3-policy-resolution.json` and `.md`;
- one durable worker receipt under `orchestration/agent_inbox/claude/`.

Do not edit AGENTS.md, D1/D2 fixtures/reports/acceptances, protected evidence,
holdout support, provider/runtime code, routes, databases, UI, deployment,
release, or write surfaces. Search only the exact named ordinary files in this
contract; broad searches across `tests` are prohibited after the documented
pre-plan incident.
