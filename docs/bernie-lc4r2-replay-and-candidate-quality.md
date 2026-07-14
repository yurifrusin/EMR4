# LC4R2 — Replay Consequence and Candidate-Quality Firewall

Date: 2026-07-14

## Objective A — Oracle-Free Replay Consequences

### Change Summary

The deterministic replay in deterministic_replay() was refactored so
that outcomes, tools, deltas, and simulated-write classification derive
ONLY from:

- The InterpretationObservation
- Synthetic diary state / initial_diary_state from the scenario
- Bounded action/outcome policy tables

All dependency on expected fields was removed:

| Expected field     | Was | Now |
|-------------------|-----|-----|
| expected_outcome_kind | Read for outcome mapping | Never read |
| expected_appointment_deltas | Read for simulated-write flag | Never read |
| expected_tool_sequence | Read in helpers | Never read |
| expected_audit_deltas | Read for simulated-write flag | Never read |
| expected_clarification | Read in helpers | Never read |

### Action-Specific Outcomes

All six diary actions now have distinct outcomes and delta change types:

| Action          | Outcome                        | Change type  |
|-----------------|--------------------------------|--------------|
| create (empty)  | appointment_created        | created  |
| create (duplicate)| existing_booking_found   | created  |
| create (overlap)| candidate_selection_required| (no deltas) |
| move            | appointment_moved          | moved    |
| resize          | appointment_resized        | resized  |
| cancel          | appointment_cancelled      | cancelled|
| status_change   | appointment_status_changed | status_changed|
| explain_schedule| schedule_explained         | (no deltas)  |
| clarification   | clarification_required     | (no deltas)  |
| unsafe/refused  | instruction_refused        | (no deltas)  |

### Fail-Closed States

Uncertain diary states (terminal, stale, concurrent,
no_slots, roster_absent, break, elapsed_window) return
None instead of producing a mutation outcome.  Negated/reversed
actions also return None with no deltas.

### Simulated-Write Classification

is_simulated_confirmed_write now derives purely from whether the
replay generated deltas:

It never reads scenario.expected_appointment_deltas.

## Objective B — Candidate-Quality Firewall

### Audit Categories

Four deterministic classification categories:

| Category | Count | Meaning |
|----------|-------|---------|
| aligned_pass | 16/30 | Surface supports label, interpreter agrees |
| aligned_failure | 8/30 | Surface supports label, interpreter disagrees |
| surface_contract_conflict | 2/30 | Explicit evidence contradicts the label |
| unsupported_or_ambiguous_surface | 4/30 | Surface text is genuinely ambiguous |

### Deterministic Rule IDs

| Rule ID | Triggers |
|---------|----------|
| CONFLICT-ACT-001 | Different intended action detected |
| CONFLICT-TMP-001 | Different temporal relation detected |
| CONFLICT-NEG-001 | Surface negation mismatches parser state |
| CONFLICT-DUR-001 | Different duration detected |
| CONFLICT-ENT-001 | Different entity state detected |
| CONFLICT-CLR-001 | Clarification state mismatch |
| CONFLICT-AUT-001 | Authority claim mismatch |
| CONFLICT-AMB-001 | Surface too ambiguous to classify |

## Owned Surface

### New Files

- app/services/bernie/development_gap_audit.py — candidate-quality
  firewall module
- scripts/bernie_lc4r_development_gap_report.py — development-only
  gap report script
- tests/test_bernie_replay_consequences.py — 25 tests for Objective A
- tests/test_bernie_development_gap_audit.py — 17 tests for Objective B

### Modified Files

- app/services/bernie/composed_evaluator.py — added
  action_negated field to InterpretationObservation
- app/services/bernie/composed_corpus_evaluator.py — Oracle-free
  replay refactoring

### Committed Artifacts

- docs/bernie-lc4r-development-gap-report.json — machine-readable
  development gap report
- docs/bernie-lc4r2-replay-and-candidate-quality.md — this document

## Verification Results

### All Tests Pass

- 89 existing evaluator tests (1 expected xfail for committed-report drift)
- 42 new focused tests (25 replay consequences + 17 development gap audit)
- 9 LC1 route regression tests

### Metrics  (LC4 development partition, 1 repeat / 1152 samples)

| Dimension | LC4R1 Baseline | Current | Delta |
|-----------|---------------|---------|-------|
| downstream_outcome | 50/1152 | 197/1152 | +147 |
| interpretation_tools | 592/1152 | 592/1152 | +0 |
| replay_tools | 592/1152 | 592/1152 | +0 |
| clarification | 610/1152 | 610/1152 | +0 |
| authority | 642/1152 | 642/1152 | +0 |
| appointment_deltas | 212/1152 | 209/1152 | -3\* |
| audit_deltas | 192/1152 | 192/1152 | +0 |
| safety | 1152/1152 | 1152/1152 | +0 |
| repeat variance | 0 | 0 | 0 |

\*\*The -3 decrease in appointment_deltas is solely explained by removing
the invented prior-write heuristic for adversarial Silver candidates.
These samples are classified as surface_contract_conflict (2) or
aligned_failure (8) in the candidate-quality audit and do not affect
any authored aligned replay regression.\*

### Report Hash

The development gap report (v2) has been generated and checked (--check
passes).

### Boundary Confirmation

- No protected holdout fixture, support module, seal receipt, or report
  was accessed
- No provider, route, database, UI, deployment, or T3 gate was modified
- No historical diary material, external dataset, or network call was used