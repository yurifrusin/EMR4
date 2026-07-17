# Bernie Synthetic Receptionist-to-Assistant Silver Corpus Contract

Date: 2026-07-17

Status: `accepted_development_silver_v1`

Authority: Yuri's multi-model development-only corpus authorization

## Product target

This corpus models instructions from a trained medical receptionist to Bernie,
not conversations between patients and receptionists. Whether typed or
dictated, the target is a comparatively constrained staff-to-assistant
language surface grounded in the existing LC semantic, policy, clarification,
replay, and safety contracts.

It does not model clinical triage, patient counselling, autonomous reception,
telephone service quality, or clinical truth. It grants no route, runtime,
provider-adapter, confirmation, database, deployment, or write authority.

## Evidence tier and protected boundary

- Every generated item is `silver/pending` discovery evidence.
- Models generate only dialogue realizations. They never generate or revise
  the semantic oracle, expected tools, diary outcome, deltas, safety boundary,
  or authority fields.
- Semantic anchors come from the ordinary LC4 development corpus through
  `app/services/bernie/synthetic_noise_corpus.py`.
- The exported manifest contains 96 hashed semantic anchors and no source
  utterances.
- Protected holdouts V1-V10 must not be opened, enumerated, listed, searched,
  imported, run, regenerated, hash-checked, inferred from, or used for tuning.
- No generated item is a certification holdout or Gold evidence.

## Generation allocation

The first attempted wave used three generator identities. It was invalidated
before integration because the Sol-owned seed exporter selected the first
multi-turn variant for 84 groups instead of the variant matching each group's
intended dialogue form. No candidate from that wave is accepted.

The corrected manifest contains exactly 12 anchors for each dialogue form:
one-shot, clarification, correction, reversal, ellipsis, anaphora, repeated,
and session restart. Every non-one-shot candidate requires at least two
receptionist turns.

The corrected recovery and review allocation is:

| Lane | Generator | Output target |
|---|---|---:|
| Sol recovery | Adopt the rejected Codex generator only as untrusted source under the recovery lease and regenerate from corrected anchors | 192 |
| Gemini review | Fresh Gemini 3.5 Flash project reviews the exact recovered candidate | 192 reviews |
| DeepSeek review | Fresh DeepSeek V4 Flash session reviews the exact recovered candidate | 192 reviews |

The recovered generation receives all 96 semantic anchors and writes exactly two candidates
per anchor:

- variant 1: `medium`, with at least two declared noise operations;
- variant 2: `high`, with at least three declared noise operations.

The same model identity cannot accept or certify its own candidates. Cross-
review uses two model identities distinct from the original Codex generator,
while Sol owns recovery, merge, quarantine, and acceptance. Gemini's first-wave generation candidate is preserved as rejected:
its own checks passed, but the Sol validator found 168 duplicate dialogue
payloads and its action templates did not represent distinct ambiguity and
dialogue contracts. It receives no same-lane generation correction loop.

## Candidate record

Each output is one JSON object per line with exactly these top-level fields:

```json
{
  "schema_version": "emr4.bernie.synthetic_noise_candidate.v1",
  "candidate_id": "deepseek_bernie_noise_seed_001_01",
  "source_seed_id": "bernie_noise_seed_001",
  "source_seed_hash": "sha256:<64 lowercase hex>",
  "generator_identity": {
    "provider_id": "deepseek",
    "model_id": "deepseek-v4-flash",
    "lane_id": "synthetic-noise-deepseek"
  },
  "variant_index": 1,
  "noise_level": "medium",
  "noise_operations": ["filler", "reordered_slots"],
  "dialogue_turns": [
    {"turn": 1, "speaker": "receptionist", "utterance": "..."}
  ],
  "evidence_spans": {
    "patient": [{"turn_index": 0, "start": 0, "end": 8, "text": "..."}]
  },
  "semantic_change": "none",
  "provenance": "silver",
  "adjudication": "pending",
  "authority_grant": {
    "provider_write": false,
    "diary_write": false,
    "confirmation": false,
    "override_authority": false
  }
}
```

`evidence_spans` must contain every key in the source seed's
`required_evidence_keys`. Every coordinate must exactly slice the generated
utterance in the named turn. It records the generated evidence, not offsets
copied from the LC source.

## Allowed noise operations

- `filler`: harmless discourse markers, politeness, or thinking words;
- `abbreviation`: ordinary staff shorthand such as `appt`, `Dr`, or `mins`;
- `typo`: a bounded, still-interpretable spelling or keyboard error;
- `punctuation_case`: punctuation, casing, or spacing variation;
- `speech_disfluency`: repetitions, false starts, or self-repair;
- `reordered_slots`: reorder patient, practitioner, date, time, or duration;
- `ellipsis`: omit syntax recoverable from the same dialogue context, without
  omitting a semantically required entity;
- `anaphora`: use a locally resolvable pronoun or noun phrase;
- `correction`: explicitly replace only the field already marked corrected by
  the frozen seed contract;
- `reversal`: explicitly withdraw only when the seed contract is reversal or
  negated;
- `temporal_surface`: equivalent Australian date/time phrasing without
  changing the frozen temporal relation or normalized value;
- `staff_shorthand`: concise diary or appointment-office phrasing;
- `dictation_artifact`: bounded transcript-like fragmentation without adding
  ASR confidence, audio, or a new semantic field;
- `distractor`: harmless operational wording that cannot be mistaken for a new
  patient, practitioner, time, duration, action, or clinical fact.

## Noise invariants

Noise may make language harder, but it must not silently change the oracle.
Every candidate must:

1. preserve the frozen intended action and action semantics;
2. preserve every normalized date, time, duration, and temporal relation;
3. preserve patient, practitioner, location, appointment-type, and duration
   semantics, including ambiguity, omission, correction, or negation;
4. preserve the dialogue state: one-shot, clarification, correction, reversal,
   ellipsis, anaphora, repeated request, or session restart;
5. introduce no new patient, practitioner, date, time, duration, action,
   appointment state, clinical condition, contact detail, or identifier;
6. make corrections and reversals explicit rather than relying on the model's
   unstated interpretation;
7. remain understandable to a competent receptionist when read in context;
8. contain only fictional LC entities and synthetic diary facts;
9. contain no instruction to bypass confirmation, identity, collision,
   authorization, audit, or native-backend authority unless that adversarial
   wording is already required by the source semantic anchor; and
10. retain all authority-grant fields as false.

High noise means more surface operations, not semantic corruption. A candidate
whose meaning is genuinely uncertain relative to its anchor must be marked for
quarantine by the reviewer; the generator must not repair the oracle.

## Generator prohibitions

Generators must not:

- access any protected holdout artifact or historical diary material;
- inspect the Kaggle appointment-call dataset or any external corpus;
- add diagnoses, symptoms, medications, Medicare numbers, phone numbers,
  addresses, email addresses, dates of birth, or other patient detail;
- create patient-facing dialogue, Bernie replies, clinical advice, or triage;
- change product code, parser behavior, policy, API, routes, database, UI,
  runtime, provider adapters, prompts, deployment, or write authority;
- report candidates as Gold, adjudicated, accepted, certified, or realistic
  reception evidence; or
- certify their own outputs.

## Mechanical acceptance before cross-review

Each lane must pass all of the following before semantic review:

- exact generator identity and owned output path;
- 192 records, two for each of 96 seed IDs;
- exact source seed hashes;
- unique candidate IDs and dialogue payloads;
- declared medium/high noise levels and minimum operation counts;
- allowlisted noise operations only;
- valid turn numbering, non-empty receptionist utterances, and exact evidence
  span coordinates;
- every required evidence key represented;
- `semantic_change=none`, `silver/pending`, and all authority fields false;
- no obvious contact identifier or clinical-detail leakage; and
- no protected, external-corpus, runtime, or write surface touched.

Mechanical validity is not semantic acceptance. Cross-review must still decide
`accept`, `quarantine`, or `reject` per candidate and state the exact reason.

## Accepted v1 claim

The accepted v1 batch contains 192 mechanically valid, independently reviewed
synthetic receptionist-to-Bernie Silver candidates over ordinary LC
development semantics. Fresh DeepSeek and Gemini reviews each accepted 192,
quarantined zero, and rejected zero on canonical hash
`sha256:ae14c613ecdd87aac39201d44a8024f3b9216f871c7d5859c4249e7f4026c665`.
Sol's bounded decision is recorded in
`tests/fixtures/bernie_synthetic_noise/admission.json`.

It does not claim real-world representativeness, clinical validation,
production readiness, Gold status, protected-holdout coverage, or new
certification coverage.
