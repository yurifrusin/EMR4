# Disposable PostgreSQL behavior function-coordinate diagnostic recovery

Date: 2026-08-08

Status: bounded diagnostic candidate; runtime closed pending fresh veto

## Evidence

Attempt 013 is preserved byte-for-byte as
`provider-free-behavior-transaction-failure-evidence-013.json`. It passed the
repaired `SERIALIZABLE` entry-point precondition and failed closed before any
scenario admission at fixed scenario `BTR-E01` with SQLSTATE `22P02`. The exact
owned container was removed and absence verified.

This proves that the isolation correction worked and that a deeper PostgreSQL
data-format rejection remains. It does not identify a particular SQL statement
or authorize a speculative SQL-artifact change.

## Closed diagnostic correction

The scenario transport already captures PostgreSQL verbose diagnostics inside
the disposable boundary. Expected-success failure handling may now release a
PL/pgSQL coordinate only when all of these conditions hold:

1. one context line is uniquely parseable;
2. the function belongs to a closed scenario-to-function allowlist;
3. the schema is exactly `emr4_context_fabric`;
4. the internal line is an integer from 1 through 100000; and
5. the evidence schema admits the exact function identifier and integer only.

Ambiguous, missing, malformed, wrong-scenario or unlisted function context
releases no coordinate. SQL text, statement type, error message, values,
signatures, paths and unrestricted identifiers remain sealed.

## Authority and next gate

No parent SQL, scenario, principal, isolation, expectation, data, container or
claim boundary changes. The correction must pass focused and hostile tests and
one fresh exact-HEAD Gemini 3.6 Flash/high veto before another newly owned
networkless disposable PostgreSQL 16 attempt. Any resulting coordinate is
diagnosis evidence only; it does not authorize weakening the accepted artifact
or scenario.
