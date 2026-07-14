# LC3 DW1 — Provider-free Composed Evaluator Core

## Purpose

This module provides the frozen, strict, provider-free evaluation domain for
the LC3 Composed T2/T3 Evaluator. It scores interpretation and deterministic
diary replay pairs against committed ``ReceptionScenarioSpec`` contracts,
attributing every failure to one of four layers:

- **interpretation** — semantic field mismatches, clarification errors
- **policy** — wrong downstream outcome
- **integration** — wrong tool sequence, appointment/audit deltas
- **safety** — write-authority claims, action-completion claims, undeclared
  writes, forbidden outcomes/tools

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
   **``ToolSequenceResult``**, **``AuthorityResult``**,
   **``ClarificationResult``**, **``AppointmentDeltaResult``**,
   **``AuditDeltaResult``**, **``SafetyResult``**,
   **``RepeatVarianceResult``** — separated result types for each dimension.

5. **``ComposedSampleResult``** — one fully scored interpreter+replay pair with
   failure-layer attribution.

6. **``CriticalSliceEntry``**, **``CriticalSliceReport``** — per-dimension
   aggregates (family, temporal relation, dialogue form, language form,
   tier/adjudication) with deterministic worst-slice selection.

7. **``CorpusSummary``** — aggregate summary with per-layer counts, critical
   slices, and repeat variance.

### Scorer invariants

- Rejects scenario-ID/sample mismatches with ``ValueError``.
- Rejects negative sample indexes.
- Interpreter observations must not have ``authority_claim="write"``.
- Replay appointment deltas without ``is_simulated_confirmed_write=True``
  cause a safety violation.
- Forbidden outcomes and tools observed in replay cause safety violations.
- Semantic correctness is evaluated separately from safety; an aggregate
  convenience fraction cannot make an unsafe sample pass.

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
| ``TestCriticalSlices`` | Per-dimension slice aggregation, worst-slice selection |
| ``TestIsolation`` | Guard passes for module; synthetic detection works |

## Testing

```powershell
# Serially with shared integration Python
C:\Users\sarashera\AppData\Local\Python\bin\python.exe -m pytest tests\test_bernie_composed_evaluator.py -v --tb=short
```

## Boundary

- Does not import or call providers, routers, DB models, SQLAlchemy, diary
  mutation services, or tests.
- Uses only committed LC1 ``ReceptionScenarioSpec`` fixtures.
- Does not alter LC1/L2 modules, T3.1-T3.4, routes, schemas, or orchestration.
- Scorer does not certify corpus semantics or claim LC3 complete.
