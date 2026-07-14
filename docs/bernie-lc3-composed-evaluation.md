# LC3 DW2 — Corpus Consumer, Deterministic Replay, Mutations, and Lattice

## Purpose

DW2 builds an offline, provider-free corpus consumer over the accepted DW1
composed-evaluator API.  It:

1. Strictly loads all 3 LC1 Gold/adjudicated scenario fixtures and all 15 LC2
   Silver/pending CorpusCandidate wrappers.
2. Preserves tier/adjudication metadata and never calls promotion logic.
3. Produces typed ``InterpretationObservation`` values through deterministic,
   provider-free language functions (``normalize_utterance``,
   ``extract_natural_time_constraints``, entity-pattern matching).
4. Replays typed semantics against synthetic state through a write-disabled
   deterministic adapter (``deterministic_replay``).
5. Scores every pair through the DW1 ``score_interpretation_replay_pair`` and
   ``build_corpus_summary``.
6. Emits a deterministic machine-readable LC3 report under ``docs/`` containing
   corpus/tier counts, per-dimension results, failure-layer counts, variance,
   critical slices, worst slice, and candidate-aware lattice counts.
7. Adds metamorphic/property checks for harmless paraphrase preservation,
   temporal minimal pairs, correction isolation, negation/unsafe preservation,
   and repeat idempotency.
8. Adds mutation checks that damage temporal relation, entity semantics,
   downstream outcome, tool sequence, authority, clarification, appointment
   delta, and audit delta — every mutation is detected and attributed to the
   expected dimension/layer.

## Module

``app/services/bernie/composed_corpus_evaluator.py``

### Corpus loading

- ``load_lc1_scenarios()`` — loads exactly 3 Gold/adjudicated fixtures from
  ``tests/fixtures/bernie_scenario_spec/``.  Rejects unknown files, wrong
  tiers/states, duplicate IDs, or incorrect counts.
- ``load_lc2_candidates()`` — loads exactly 15 Silver/pending wrappers from
  ``tests/fixtures/bernie_corpus_candidates/`` (5 family files with 3 each).
  Rejects duplicate IDs, wrong tiers/states, or incorrect per-family counts.

### Deterministic interpretation

``deterministic_interpret(scenario)`` produces an ``InterpretationObservation``
using:

- ``normalize_utterance`` for lossless NFKC normalization with time-form
  detection.
- ``extract_natural_time_constraints`` and ``parse_time_fragment`` from
  ``app/services/diary/temporal.py`` for temporal extraction.
- Simple entity-pattern matching for patient/practitioner/duration extraction.
- Multi-turn state reducer: correction turns replace only the corrected field;
  other fields carry forward losslessly.
- Unsafe/bypass wording detection before ordinary intent matching.
- Missing/ambiguous required information triggers clarification.
- Authority is always ``read``, ``clarify``, or ``refuse`` — never ``write``.
- Never copies expected scenario fields into the observation.

### Deterministic replay

``deterministic_replay(scenario, interpretation)`` produces a
``ReplayObservation`` using:

- Outcome mapping based on interpretation state and scenario diary state.
- Tool sequence derived from interpretation tools.
- Appointment/audit deltas derived from interpretation values (not expected).
- Simulated confirmed write flags for scenarios with declared creation.
- Forbidden outcome/tool observation checks.

### Report

``evaluate_corpus()`` runs the full pipeline and returns a deterministic
report dict with:

- Schema version and corpus manifest/counts.
- All 18 scenario IDs with tier/adjudication posture.
- Per-dimension pass/fail counts (interpretation, policy, integration, safety).
- All-layer failure counts and repeat variance.
- Critical slices and deterministic worst slice.
- Per-case compact findings.
- Candidate-aware lattice summary.

``generate_report_json()`` returns the JSON string.

## CLI

``scripts/bernie_lc3_composed_eval.py`` — usage:

```
python scripts/bernie_lc3_composed_eval.py
python scripts/bernie_lc3_composed_eval.py --lc1-dir <path> --lc2-dir <path>
python scripts/bernie_lc3_composed_eval.py --output <path>
```

Generates ``docs/bernie-lc3-composed-evaluation-report.json``.

## Candidate-aware lattice

The ``scripts/bernie_coverage_lattice.py`` script has a new
``--candidate-dir`` option for candidate-aware mode:

```
python scripts/bernie_coverage_lattice.py --candidate-dir tests/fixtures/bernie_corpus_candidates
```

The default LC1 CLI output remains byte-for-byte/schema backward compatible.
When ``--candidate-dir`` is specified, the report includes a
``candidate_aware_lattice`` block with:

- adjudicated scenario/covered/empty counts
- candidate counts by tier and adjudication
- candidate-only covered cell count plus bounded examples
- union covered/empty counts
- proof that pending/quarantined candidates do not reduce the adjudicated
  empty-cell count

The total lattice remains 152,064.

## Tests

``tests/test_bernie_composed_corpus_evaluator.py``:

| Test class | Coverage |
|---|---|
| ``TestLoadLC1Scenarios`` | Strict loading, correct count, gold/adjudicated tiers |
| ``TestLoadLC2Candidates`` | Strict loading, correct count, silver/pending tiers |
| ``TestDeterministicInterpret`` | Valid InterpretationObservation, authority never write |
| ``TestDeterministicReplay`` | Valid ReplayObservation, no undeclared writes |
| ``TestCorpusEvaluation`` | Full report shape, deterministic stability, lattice counts |
| ``TestCommittedReportMatch`` | Regenerated report matches committed artifact |
| ``TestIsolation`` | No prohibited imports in evaluator module |

``tests/test_bernie_lc3_mutations.py``:

| Test class | Coverage |
|---|---|
| ``TestMetamorphicParaphrase`` | Paraphrase preserves semantics where supported |
| ``TestMetamorphicMinimalPair`` | Temporal minimal pairs change only intended fields |
| ``TestMetamorphicCorrection`` | Correction turns change only one field |
| ``TestMetamorphicUnsafe`` | Unsafe wording always refused |
| ``TestMetamorphicIdempotent`` | Repeated requests produce same outcome |
| ``TestMutationTemporalRelation`` | Damaged temporal → interpretation failure |
| ``TestMutationEntitySemantic`` | Damaged entity → interpretation failure |
| ``TestMutationOutcome`` | Damaged outcome → policy failure |
| ``TestMutationInterpretationTools`` | Damaged interp tools → integration failure |
| ``TestMutationReplayTools`` | Damaged replay tools → integration failure |
| ``TestMutationAuthority`` | Unsafe authority → safety failure |
| ``TestMutationClarification`` | Damaged clarification → interpretation failure |
| ``TestMutationAppointmentDelta`` | Damaged appt delta → integration failure |
| ``TestMutationAuditDelta`` | Damaged audit delta → integration failure |
| ``TestMutationMultiLayer`` | Multiple mutations → multiple layers |

## Report

The committed report is at
``docs/bernie-lc3-composed-evaluation-report.json``.  It is generated
deterministically with no wall-clock timestamp.

### Actual counts (DW2 revision)

| Metric | Value |
|---|---|
| Scenarios | 18 (3 LC1 Gold + 15 LC2 Silver) |
| Samples (2× repeat) | 36 |
| Passed | 24 (67%) |
| Failed | 12 (33%) |
| Safety failures | 0 |
| Policy failures | 0 |
| Interpretation failures | 22 (all-layer) |
| Integration failures | 10 (all-layer) |
| Variant scenarios | 0 (deterministic adapter) |

### Per-dimension breakdown (36 samples)

| Dimension | Passed | Failed |
|---|---|---|
| intended_action | 24 | 12 |
| action_semantics | 36 | 0 |
| temporal_relation | 30 | 6 |
| normalized_values | 28 | 8 |
| entity_semantics | 34 | 2 |
| requires_clarification | 36 | 0 |
| downstream_outcome | 36 | 0 |
| interpretation_tools | 26 | 10 |
| replay_tool_sequence | 26 | 10 |
| authority | 36 | 0 |
| appointment_deltas | 36 | 0 |
| audit_deltas | 36 | 0 |
| safety | 36 | 0 |

### Metamorphic evidence

6/6 checks pass: paraphrase variants, minimal temporal/duration pairs,
correction isolation, unsafe preservation, and idempotency.

### Mutation evidence

9/9 checks pass: temporal relation, entity semantic, downstream outcome,
interpretation tools, replay tools, authority, clarification, appointment
delta, and audit delta mutations are all correctly detected with the
expected attribution layer.

### Candidate-aware lattice

| Metric | Value |
|---|---|
| Adjudicated cells | 3 |
| Adjudicated empty | 152061 |
| Candidate-only cells | 7 |
| Union covered cells | 10 |
| Union empty cells | 152054 |
| Total lattice | 152064 |
| Gaps preserved | True |

### Remaining gaps

Failures are honest (not oracle-echo):
- **temporal_relation** (3 scenarios × 2 repeats = 6): the ambiguity
  scenarios expect ``interval`` for "sometime in the afternoon" but the
  deterministic interpreter returns ``unspecified`` (consistent with the LC1
  reference which also uses ``unspecified`` for the same phrase).  This is a
  documented semantic inconsistency between fixtures — preserved, not branched.
- **normalized_values** (4 scenarios × 2 repeats = 8): flows from the same
  temporal mismatch plus one scenario with no explicit time/duration.
- **entity_semantics** (1 scenario × 2 repeats = 2): the LC1 overlap/correction
  scenario's entity extraction does not reach the patient name in the
  correction-turn interval format.
- **intended_action** (6 scenarios × 2 repeats = 12): scenarios where
  clarification/temporal ambiguity was detected; the observed action is
  ``None`` because the system correctly identifies ambiguity before
  committing to an action.
- **interpretation_tools** / **replay_tools** (5 scenarios × 2 repeats = 10):
  tool sequence alignment differs from expected in clarification and
  correction scenarios where the system's deterministic tool selection does
  not match the adjudicated expectation.

No safety, policy, authority, clarification delta, or outcome failures.
Zero repeat variance confirms the deterministic adapter is stable.

### Boundary

- No provider SDK, provider adapter, live prompt, or external call.
- No route, GraphQL, OpenAPI, database model, migration, or appointment/audit
  persistence.
- No historical-diary access, H-series/H15 import, memory, RAG, or GraphRAG.
- No external dataset download, licence acceptance, or PHI.
- No modification of LC1/LC2 fixtures, T3.1-T3.4, providers, routes, DB/models,
  UI, runtime gates, or historical data.
- Never calls promotion logic; Silver pending is never described as truth.
- Authority ``write`` is rejected by the ``InterpretationObservation``
  constructor (fail-closed).
