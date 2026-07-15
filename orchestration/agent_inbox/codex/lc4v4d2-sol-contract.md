# LC4V4D2 Sol Contract — Bounded Semantic Remediation

Date: 2026-07-15

Authority: ordinary development continuation from accepted LC4V4D1. GPT Sol
owns the plan, semantic architecture, acceptance, recovery, and protected
integration. DeepSeek V4 Flash/high through Claude Code `--bare` is the single
bounded implementation/test worker. Gemini 3.5 Flash through a fresh
Antigravity project is the independent veto reviewer. DeepSeek Pro is not
authorized.

## Objective

Repair only the utterance-level semantic interpretation defects proved by the
23-case LC4V4D1 parser selection. Preserve the D1 fixture population and
historical report as immutable baseline evidence. Do not repair or relabel the
12 D1 policy/state-join cases in this sprint.

Source baseline:

- D1 fixture hash:
  `sha256:a81de0b5371d4fcc425c23f0da9560e29827e3e85cc22847990ea83518863269`
- D1 report hash:
  `sha256:1527b99359dc76e831d7eabf49fff022781faf5d248c436bde6e022f30eff84d`
- Frozen 23-case selection hash:
  `sha256:1b254ae627e26b1b301b660628d90f39dce5e0364afc0cfcf4c4855fb6531f02`

## Exact target selection

Entity semantics (12):

- `lc4v4d1_entity_patient_omitted_02`
- `lc4v4d1_entity_patient_ambiguous_03`
- `lc4v4d1_entity_patient_negated_05`
- `lc4v4d1_entity_practitioner_ambiguous_09`
- `lc4v4d1_entity_practitioner_negated_11`
- `lc4v4d1_entity_location_ambiguous_15`
- `lc4v4d1_entity_location_negated_17`
- `lc4v4d1_entity_appt_type_ambiguous_21`
- `lc4v4d1_entity_appt_type_negated_23`
- `lc4v4d1_entity_duration_ambiguous_27`
- `lc4v4d1_entity_duration_corrected_28`
- `lc4v4d1_entity_duration_negated_29`

Dialogue/trajectory semantics (5):

- `lc4v4d1_dialogue_clarification_multi_02`
- `lc4v4d1_dialogue_correction_single_03`
- `lc4v4d1_dialogue_reversal_single_05`
- `lc4v4d1_dialogue_ellipsis_multi_08`
- `lc4v4d1_dialogue_session_restart_multi_12`

Safety-pair base semantics (6):

- `lc4v4d1_safety_move_safe_03`
- `lc4v4d1_safety_move_unsafe_04`
- `lc4v4d1_safety_resize_safe_05`
- `lc4v4d1_safety_resize_unsafe_06`
- `lc4v4d1_safety_explain_safe_11`
- `lc4v4d1_safety_explain_unsafe_12`

No other D1 case may be used to justify a semantic change. Existing ordinary
tests may be used only as regression evidence.

## Required semantic behavior

Implement the narrowest composable rules that satisfy these explicit surfaces:

1. For create, omitted required patient identity fails closed to clarification.
2. Explicit `A or B` alternatives classify only the named target entity as
   ambiguous and do not silently select one alternative.
3. Explicit target exclusions classify that entity as negated and do not leave
   the excluded value as the resolved normalized value.
4. Duration alternatives remain ambiguous; an explicit correction replaces the
   former duration; an excluded duration is removed from final normalization.
5. A later exact clarification turn resolves a compatible earlier broad time
   period without requiring a correction keyword.
6. Inline corrections resolve the replacement entity while retaining lossless
   evidence of both values.
7. Elliptical continuation carries forward prior patient/practitioner facts;
   a session restart discards abandoned facts and uses only the new request.
8. Inline and multi-turn explicit reversal cues set `action_negated` without
   converting the underlying intended action into a different diary action.
9. Move normalization uses the final target date/time, not the source slot.
10. The explicit verb `resize` maps to resize semantics.
11. A practitioner possessive such as `Dr Chen's schedule` is not patient
    identity evidence.
12. Adding the matched `Do not bypass confirmation` or `Bypass confirmation`
    clause may change only safety/action posture and authority behavior; it must
    not change the base action, temporal, or entity parse.

Rules must be boundary-aware and covered by positive and false-positive tests.
Do not add phrase-specific scenario-ID branches, copy expected fixture fields,
inspect scorer expectations during interpretation, or broaden a regex beyond
the supported grammatical relation.

## Explicit exclusions

Do not modify:

- `deterministic_replay`, replay outcome/delta policy, composed scorer logic,
  expected authority derivation, or tool policy tables;
- the frozen D1 fixture files, D1 JSON/Markdown report, D1 hashes, or D1
  acceptance;
- the five explicit mismatched diary-state joins, corrected-patient tool
  policy, practitioner-ID replay policy, or unsafe refusal-tool policy;
- any protected holdout v1-v4 file, support module, manifest, seal, receipt,
  test, path population, or case-level surface;
- `check_in`, T3.1-T3.5, providers, routes/APIs, databases, historical diary,
  UI, deployment, release, confirmation, or runtime write behavior.

Holdouts v1-v4 remain sealed. No protected file may be opened, enumerated,
listed, searched, imported, run, regenerated, evaluated, hash-checked, inferred
from, or tuned against.

## Evidence implementation

Add a small D2 evaluator/report that:

- validates the exact frozen D1 fixture/report/selection hashes and the exact
  23 IDs before running current code;
- records before/after classification and failed semantic fields for all 23
  targets plus regression status for all 60 fixed probes;
- runs every current observation twice and compares complete normalized
  fingerprints with only `sample_index` removed;
- reports any new parser gap outside the frozen target selection;
- preserves the committed D1 report unchanged;
- emits a complete inspectable D2 JSON and concise Markdown report; and
- never authorizes policy remediation or any holdout action.

The D1 test may be changed only to distinguish immutable baseline-artifact
assertions from live post-remediation regression assertions. It must continue
to validate the frozen D1 hashes and fixture population. Historical D1 evidence
must not be regenerated.

## Acceptance

LC4V4D2 is acceptable only if:

- all 23 target cases have no utterance-level semantic mismatch on both repeats;
- current D1 evaluation has zero `parser_gap`, zero `authoring_invalid`, zero
  scorer-only defects, and zero variance;
- every formerly supported D1 case remains supported;
- no new parser gap appears outside the frozen target selection;
- the five mismatched diary joins remain policy-contract gaps rather than being
  faked inside the utterance parser;
- policy-only cases are disclosed and not counted as semantic failure;
- focused semantic, D1/D2 evidence, handover, and adjacent deterministic suites
  pass serially, with immutable historical equality nodes deselected rather
  than regenerated; and
- Gemini independently returns `DECISION: pass` on the exact recovered head.

A failure may produce a smaller supported subset, but Sol must not weaken the
oracle or relabel a case merely to reach zero. Parser remediation ends at the
semantic boundary; policy/state-join work requires a separate later contract.

## Owned paths

- `app/services/bernie/semantic_extraction.py`
- `app/services/bernie/lc4v4d2_semantic_remediation.py`
- `tests/test_bernie_lc4v4d2_semantic_remediation.py`
- narrowly required updates to
  `tests/test_bernie_lc4v4d1_development_diagnostic.py`
- `docs/bernie-lc4v4d2-semantic-remediation.json`
- `docs/bernie-lc4v4d2-semantic-remediation.md`
- one durable worker receipt under `orchestration/agent_inbox/claude/`

The worker must not edit `AGENTS.md`, this contract, D1 fixtures/reports/
acceptance, replay/scorer/policy modules, protected evidence, or any product
surface outside the owned paths.
