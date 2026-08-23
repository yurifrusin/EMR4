# Raisa traceable synthetic scenario envelope and legacy binding rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T00:51:49.7346365+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-traceable-synthetic-scenario-envelope-and-legacy-binding-rehearsal`

Planning source HEAD: `7a3f6b5f7d9d2850a0c5c2be098f21c4009c8523`

Reasoning level: Extra High. This tranche creates a reusable evidence boundary
that later privacy-calibrated scenarios will depend on, while preserving two
accepted and differently shaped reception test contracts without duplicating
either one.

## Objective

Implement the smallest strict, domain-neutral traceability envelope that can
bind one authored-synthetic scenario identity to existing semantic and
executable representations. Prove it against the two existing non-protected
Reception pairs:

- `booking_create_then_exact_duplicate`; and
- `booking_overlap_not_exact_duplicate`.

The envelope records provenance, oracle eligibility, coverage, role separation
and exact execution references. It is development evidence only. It grants no
product, provider, data, command or runtime authority.

Immediately after this tranche passes, launch
`raisa-local-only-historical-diary-snapshot-privacy-feasibility-review`. That
successor begins with authored-synthetic snapshot fixtures. This tranche must
not open, list, search, sample, hash, parse or otherwise inspect the historical
Diary trove.

## Exact schema

Create `orchestration_harness/synthetic_scenario_envelope.py` as a pure Pydantic
module with `extra="forbid"`, frozen records and closed vocabularies.

The schema contains:

1. eight source-type tokens implementing the seven accepted authority classes:
   `normative_or_clinical_guidance`, `accepted_emr4_contract`,
   `method_or_interoperability_standard`, `vendor_operational_documentation`,
   `vendor_advertised_capability`, `fiction_prompt_only`,
   `private_observed_calibration` and `local_design_assumption`;
2. derived, closed oracle-eligibility values that a source record cannot
   self-promote;
3. four distinct evidence labels: `wholly_authored_synthetic`,
   `synthetic_calibrated_from_private_aggregates`,
   `deidentified_observed_sequence` and `raw_private_observation`;
4. typed `OracleBundle` entries separating deterministic truth,
   authority/safety rules and model-quality rubrics;
5. typed `CoverageClaim` entries with closed coverage kinds;
6. author, extractor, adjudicator and reviewer assignments with four distinct
   identities; a model may be an extractor but may not author, adjudicate or
   review an authoritative oracle;
7. an optional `CalibrationEvidenceRef` whose grammar permits only an opaque
   local token and whose typed fields require `resolvable=false` and
   `deidentification_claimed=false`; and
8. an execution binding containing shared scenario identity, complementary-
   representation relation, repository-relative paths and exact SHA-256
   digests only. It contains no dialogue, state, action or expected-outcome
   payload.

Source records require a locator, issuer, title, jurisdiction, version or
retrieval fact, rights posture, transformation, supported claims and
limitations. Oracle eligibility is computed from source type. Normative or
clinical sources require scope review; accepted EMR4 contracts may bind an
accepted-contract oracle; method, vendor, fiction, private-observation and
local-assumption sources cannot bind authoritative oracles.

The first schema version admits executable bindings only when the evidence
label is `wholly_authored_synthetic`. Later admission of a de-identified or
privately calibrated case requires an explicit schema revision after the Diary
privacy gate; declaring a different evidence label cannot silently gain
execution eligibility.

## Exact non-duplicative bindings

Create one development fixture manifest under
`tests/fixtures/raisa_synthetic_scenario_envelope/`. It contains two envelopes
and only traceability metadata. The exact bound payloads are:

| Scenario | Semantic fixture SHA-256 | Replay fixture SHA-256 |
|---|---|---|
| `booking_create_then_exact_duplicate` | `0d90a7adc20663a122946dbabb89f691a2165f3caf5db0b60628728adf9c075d` | `c6fbd8105922fcbb9a8b7bee94d67f757a8bc86a315abc1464f8b95f377a48c1` |
| `booking_overlap_not_exact_duplicate` | `ba0ebf78944e892d447bc4cd6aab9f524f62751f3f7ebd5150c93fa9a7cb6510` | `ca098a054883bb90199a6aa29e18a181b4d36a9bf887dcc197927e0f793a90d5` |

The validator has a hard-coded allowlist of those four repository-relative
paths. It resolves paths beneath an explicitly supplied repository root,
rejects traversal and symlinks escaping that root, compares bytes to the
declared digest, loads the JSON through `ReceptionScenarioSpec`, loads the YAML
through `tests.bernie_scenarios.loader.load_scenario_yaml`, and requires both
loaded identities to equal the envelope identity. It must not discover or glob
fixtures and must not import or execute the replay engine.

The pair relationship is `complementary_shared_identity`: semantic JSON owns
the meaning and expected deterministic behaviour; YAML owns its executable
stateful rehearsal. The validator does not claim field-for-field equivalence.

## Hostile tests

Create `tests/test_raisa_traceable_synthetic_scenario_envelope.py` covering:

- strict version, extra-field and closed-vocabulary rejection;
- source-type-to-oracle-eligibility derivation and self-promotion rejection;
- missing locator, rights posture, transformation or limitation rejection;
- vendor-advertised and fiction sources rejected from deterministic-truth and
  authority/safety oracles;
- model author, adjudicator and authoritative reviewer rejection while a
  distinct model extractor remains representable;
- repeated role identity rejection;
- protected/path/URL/hash-shaped calibration references rejected, along with
  any `resolvable` or de-identification claim;
- non-wholly-authored executable binding rejection;
- traversal, non-allowlisted path, digest mutation and scenario-ID mismatch
  rejection;
- both exact legacy pairs loading through their existing owners; and
- manifest serialization containing no copied dialogue, turns,
  `initial_diary_state`, `expected_outcome_kind` or patient/practitioner names.

Focused verification also reruns `tests/test_bernie_scenario_spec.py` and
`tests/bernie_scenarios/test_t1_stateful_contract.py` to prove the existing
contracts remain unchanged.

## Acceptance

Pass requires:

1. a fresh five-source Ariadne receipt and valid in-progress latch;
2. explicit DeepSeek, Gemini and native-subagent dispositions;
3. strict typed validation and all hostile tests passing;
4. both legacy pairs validating by exact reference without copied payload;
5. no product source, route, client, database, configuration, replay engine or
   existing fixture change;
6. no historical Diary, protected evidence, provider/model or network access;
7. a passing clockwork closeout, paired lay/technical Yuri summary and non-PHI
   Pushover notification; and
8. unchanged protected refs and preservation of every unrelated untracked
   file.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The occupied native harness is
  paused pending separate boot proof; this tightly coupled schema/validator
  package has no safe isolated worker lease and Claude Code is not a silent
  transport fallback.
- **Gemini:** not applicable with neutral leverage. The active latch prohibits
  live provider/model execution, so no review packet may be dispatched.
- **Native subagents:** declined with negative leverage. Schema, manifest and
  validator tests form one serially coupled invariant and there is no owned
  independent package in this tranche.
- **GPT Sol:** owns implementation, hostile testing, exact Git binding,
  acceptance, clockwork publication and successor-latch transition.

## Closed surfaces

Provider-free and unmounted. No historical Diary open/list/search/sample/hash/
parse, real or real-practice-derived fixture, protected holdout/support access,
private-calibration resolution, patient/appointment/clinical/product data,
product runtime/route/API/client/database/configuration change, ordinary-
practice enablement, provider/model prompt or cost, production, deployment,
release, Pages or protected-ref movement. Local/origin `master` and
`handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only.
