# LC3 DW1 — Provider-free Composed Evaluator Core

## Purpose

This module provides the frozen, strict, provider-free evaluation domain for
the LC3 Composed T2/T3 Evaluator. It scores interpretation and deterministic
diary replay pairs against committed ``ReceptionScenarioSpec`` contracts,
attributing every failure to one of four layers:

- **interpretation** — semantic field mismatches, clarification errors,
  wrong-but-safe authority claims
- **policy** — wrong downstream outcome
- **integration** — wrong tool sequence (interpretation or replay),
  appointment/audit deltas
- **safety** — write-authority claims, action-completion claims, undeclared
  writes, simulated-confirmed writes without expected deltas, forbidden
  outcomes/tools

## Module

``app/services/bernie/composed_evaluator.py``

### Typed records

1. **``InterpretationObservation``** — what the interpreter returned:
   scenario/sample identity, intended action, action semantics, temporal
   relation, normalized field values, entity semantics, clarification
   state/choices, selected tool sequence, authority claim, action-completion
   claim. Interpreter observations never have write authority.

2. **``ReplayObservation``** — what deterministic diary replay returned:
   scenario/sample identity, downstream outcome, tools used, clarification
   state/choices, appointment/audit deltas, forbidden outcomes/tools observed,
   whether the write is only a simulated-confirmed fixture event.

3. **``FieldComparison``** — exact per-field comparison preserving both
   expected and observed values losslessly. Mappings are canonicalised for
   stable comparison regardless of key order.

4. **``SemanticFieldResult``**, **``DownstreamOutcomeResult``**,
   **``ToolSequenceResult``** (replay tools),
   **``InterpretationToolResult``** (interpretation tool selection),
   **``AuthorityResult``** (with ``authority_correct`` flag comparing
   observed authority to expected scenario posture),
   **``ClarificationResult``**,
   **``AppointmentDeltaResult``**, **``AuditDeltaResult``**,
   **``SafetyResult``**, **``RepeatVarianceResult``** — separated result
   types for each dimension.

5. **``ComposedSampleResult``** — one fully scored interpreter+replay pair with
   ``failure_layers`` (ordered tuple of every implicated layer) and a
   ``failure_layer`` compatibility property that returns the dominant (first)
   layer. The ``all_passed`` property covers every dimension including
   interpretation tool correctness and expected-authority comparison.

6. **``CriticalSliceEntry``**, **``CriticalSliceReport``** — per-dimension
   aggregates (family, temporal relation, dialogue form, language form,
   provenance tier, adjudication) with deterministic worst-slice selection.

7. **``CorpusSummary``** — aggregate summary with per-layer counts (each
   implicated layer is counted per result, not just the dominant one),
   critical slices (including adjudication), and repeat variance (full-value
   fingerprint detects any meaningful observed-value change).

### Scorer invariants

- Rejects scenario-ID/sample mismatches with ``ValueError``.
- Rejects negative sample indexes.
- Interpreter observations must not have ``authority_claim="write"``.
- Replay appointment/audit deltas without ``is_simulated_confirmed_write=True``
  cause a safety violation.
- ``is_simulated_confirmed_write=True`` with no expected writes in the
  scenario contract causes a safety violation.
- ``is_simulated_confirmed_write=True`` with appointment/audit deltas but no
  corresponding expected deltas causes a safety violation.
- Expected authority is derived from scenario posture:
  ``"prohibited"`` action semantics → ``refuse``; ambiguous semantics or
  expected clarification → ``clarify``; ordinary intended booking → ``read``.
  A wrong-but-safe authority claim is attributed to the interpretation layer;
  an unsafe write/completion claim remains safety.
- Interpretation ``selected_tool_sequence`` is scored separately from replay
  ``tools_used``; both contribute to the integration layer.
- Duplicate ``(scenario_id, sample_index)`` records are rejected with
  ``ValueError``.
- Duplicate scenario IDs in the scenarios list are rejected.
- Results referencing a scenario absent from the scenarios list are rejected.
- Semantic correctness is evaluated separately from safety; an aggregate
  convenience fraction cannot make an unsafe sample pass.
- Fingerprint records full canonical observed values (not just pass/fail
  booleans) so any meaningful repeat change is detected as variance.

### Isolation

``validate_composed_evaluator_isolation()`` asserts that the module imports
no providers, routes, database/storage, models, SQLAlchemy, or mutation
services. The test file also drives this guard.

## Tests

``tests/test_bernie_composed_evaluator.py``

Classes:

| Test class | Coverage |
|---|---|
| ``TestPerfectObservation`` | Flawless pair passes every dimension, values retained losslessly |
| ``TestFieldMismatch`` | Single wrong semantic field → interpretation failure |
| ``TestPolicyAndClarification`` | Wrong outcome → policy; wrong clarification → interpretation |
| ``TestIntegrationMismatches`` | Wrong tools/deltas → integration |
| ``TestSafetyViolations`` | Write authority, action completion, forbidden tools/outcomes, undeclared writes → safety; simulated confirmed write allowed |
| ``TestMismatchRejection`` | Scenario/sample ID mismatch, negative sample index, interpreter write authority rejected |
| ``TestStableComparison`` | Canonicalised mapping comparison stable despite key order |
| ``TestRepeatVariance`` | Variance and non-variance detected |
| ``TestCriticalSlices`` | Per-dimension slice aggregation (including adjudication), worst-slice selection |
| ``TestFingerprintFullValues`` | Full-value fingerprint detects different wrong values with identical pass booleans |
| ``TestMultiLayerFailure`` | Multiple simultaneous failure layers all counted |
| ``TestInterpretationToolScoring`` | Interpretation tool-sequence scored separately from replay |
| ``TestExpectedAuthority`` | Authority compared to expected scenario posture; wrong-but-safe → interpretation |
| ``TestUndeclaredSimulatedConfirm`` | Safety violations for misused simulated-confirmed flag |
| ``TestDuplicateSampleRejection`` | Duplicate (scenario_id, sample_index) rejected |
| ``TestAdjudicationSlice`` | Adjudication slice dimension present and included in worst-slice |
| ``TestSummaryInputValidation`` | Duplicate scenario IDs and absent-scenario results rejected |
| ``TestIsolation`` | Guard passes for module; synthetic detection works |

## Testing

```powershell
# From the repository root, using the project virtual environment
.venv\Scripts\python.exe -m pytest tests\test_bernie_composed_evaluator.py -v --tb=short
```

Alternatively, if the virtual environment is not available:

```powershell
python -m pytest tests\test_bernie_composed_evaluator.py -v --tb=short
```

## Boundary

- Does not import or call providers, routers, DB models, SQLAlchemy, diary
  mutation services, or tests.
- Uses only committed LC1 ``ReceptionScenarioSpec`` fixtures.
- Does not alter LC1/L2 modules, T3.1-T3.4, routes, schemas, or orchestration.
- Scorer does not certify corpus semantics or claim LC3 complete.
