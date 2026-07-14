# LC4R7 Silver Contract-Quality Reconciliation

**Date:** 2026-07-15
**Role:** DeepSeek V4 Flash/high implementation/test worker (bounded reconciliation)
**Conductor/acceptance:** GPT Sol
**Independent review:** Gemini 3.5 Flash (pending)

## Summary

This sprint consolidates the residual normalization, entity, temporal, action, and
clarification audits from LC4R1–LC4R6 into one deterministic 1,436-record
adjudication queue. The queue classifies every aligned-failure scenario from the
development corpus into exactly one disposition per failed semantic field,
using only the public development audit and composed evaluator.

## Frozen selection

The ordinary development audit (`development_gap_audit.audit_candidates`)
selects exactly **572** scenarios as `aligned_failure`. The frozen selection
hash is `e17eb1739c16f3de`.

Each scenario is interpreted and replayed at one repeat through the composed
evaluator. For every failed semantic field, one queue record is emitted. For
scenarios where all semantic fields pass but the composed replay still fails,
a single `replay_contract` record is emitted.

## Queue taxonomy

1,436 records in `docs/bernie-lc4r7-adjudication-queue.json`:

| Dimension | Disposition | Count |
|---|---|---|
| intended_action | planned_not_implemented | 26 |
| action_semantics | planned_not_implemented | 39 |
| action_semantics | contradictory | 78 |
| temporal_relation | malformed | 66 |
| temporal_relation | incomplete | 18 |
| temporal_relation | contradictory | 75 |
| normalized_values | malformed | 66 |
| normalized_values | incomplete | 220 |
| normalized_values | contradictory | 45 |
| normalized_values | mixed_contract_defect | 146 |
| entity_semantics | incomplete | 374 |
| entity_semantics | contradictory | 17 |
| entity_semantics | mixed_contract_defect | 58 |
| requires_clarification | planned_not_implemented | 26 |
| requires_clarification | contradictory | 78 |
| requires_clarification | requires_adjudication | 53 |
| replay_contract | non_language_contract_mismatch | 51 |

Zero `surface_supported_parser_gap` records.

## Classification logic

Each dimension failure is classified using deterministic rules:

### Temporal relation
- **malformed (66):** `_extract_temporal` returns `unspecified` but the utterance
  contains a dangling `after`/`before`/`between`/`around` operator.
- **incomplete (18):** No extractable temporal relation or operator.
- **contradictory (75):** Extracted surface relation differs from contract.

### Normalized values
- **malformed (66):** Dangling temporal operator + missing time source span.
- **incomplete (220):** Expected normalized value has no source span.
- **contradictory (45):** Value has source span but differs from contract, or
  interpreter produces value absent from contract.
- **mixed_contract_defect (146):** Both incomplete and contradictory fields
  in the same scenario.

### Entity semantics
- **incomplete (374):** Interpreter cannot determine an entity value (returns
  `omitted` or `ambiguous`) when the contract expects a concrete value.
- **contradictory (17):** Both interpreter and contract have concrete but
  differing entity values.
- **mixed_contract_defect (58):** Both incomplete and contradictory entity
  fields in the same scenario.

### Intended action / action semantics
- **planned_not_implemented (26/39):** Scenario is a `check_in` surface.
  `check_in` is deliberately unimplemented in the native Diary grammar.
- **contradictory (0/78):** Interpreter action differs from contract.

### Requires clarification
- **planned_not_implemented (26):** `check_in` surface with clarification failure.
- **contradictory (78):** Interpreter produces clarification when contract
  does not expect it.
- **requires_adjudication (53):** Contract expects clarification but
  interpreter does not produce it. Requires human review.

### Replay contract
- **non_language_contract_mismatch (51):** All semantic fields pass but
  downstream replay (outcome, tools, deltas, authority) disagrees.

## Check-in preservation

All 39 native `check_in` surfaces are classified as `planned_not_implemented`:

- **26** fail `intended_action` (the extractor cannot map `check_in` to any
  known action).
- **13** are near-matches where `intended_action` is correctly detected as
  `status_change` but `action_semantics` still fails.

## Exit gate

The language-bridge exit gate remains
`blocked_pending_adjudication_and_contract_reconciliation`:

- **53** clarification-policy records require independent human adjudication.
- **51** semantic-pass records require non-language replay/delta contract
  reconciliation.
- All remaining residuals are malformed, incomplete, contradictory, mixed, or
  planned-not-implemented Silver evidence.
- Zero parser-supported gaps exist.

## Current baselines

| Dimension | Count |
|---|---|
| intended action | 880/1152 |
| action semantics | 814/1152 |
| temporal relation | 628/1152 |
| normalized values | 101/1152 |
| entity semantics | 300/1152 |
| clarification | 782/1152 |
| safety | 1152/1152 (zero variance over 2304 samples) |

## Boundaries

- Ordinary LC4 development partition only (Silver/pending).
- No protected holdout v1 accessed, enumerated, or evaluated.
- No provider calls, routes, API, database, UI, deployment, or write authority.
- No fixture or generator modifications.
- No source-span field names treated as interpreter truth.
- `check_in` preserved as planned-not-implemented.
- T3.1–T3.4 intact; T3.5 providers and all live/write authority deferred.

## Files

- `scripts/bernie_lc4r7_silver_reconciliation.py` — reconciliation helper
  with `--check`
- `tests/test_bernie_lc4r7_silver_reconciliation.py` — focused tests
- `docs/bernie-lc4r7-adjudication-queue.json` — committed 1,436-record queue
- `docs/bernie-lc4r7-silver-reconciliation-report.json` — committed report
- `docs/bernie-lc4r7-silver-reconciliation.md` — this note
- `orchestration/agent_inbox/codex/lc4r7-dw1-completion.md` — completion artifact
