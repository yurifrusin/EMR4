# Threat-model delta: Bureau explicit-selection retry readiness

Status: provider-free maintenance boundary
Recorded: 2026-07-31

## New risk examined

An utterance can name a patient and practitioner yet still fail to identify the
exact appointment. A test harness that assumes selection can cause the model
to receive less context than the operator sees.

## Controls

- Selection must be an actual browser click on one exact disposable
  authored-synthetic appointment row.
- The row must report `aria-selected=true` before submission.
- The request body is observed only as a closed planner mode, selection
  presence boolean and canonical hash.
- No raw appointment identifier is retained in the tranche evidence.
- The provider is disabled and deterministic fallback is not relevant because
  deterministic planning is selected directly.
- The route, proofreader and adapter remain proposal-only and non-writing.
- Database before/after counts and hashes must match.
- The harness owns one exact database and temporary runtime root and removes
  both.

## Closed boundaries

Provider calls, credentials, model runtime, real/product/patient/health/
clinical/historical data, confirmation, writes, external delivery, production,
deployment and release remain closed.
