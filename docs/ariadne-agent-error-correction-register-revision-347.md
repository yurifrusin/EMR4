# Ariadne agent error and correction register — revision 347

Date: 2026-08-18

Timestamp: 2026-08-18T03:42:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 347 adds AER-0398. The first provider-free post-cancellation
orientation preplanning state used the invented Gemini `expected_leverage`
value `conditional_independence`. The repository-local preflight rejected it
before plan freeze, dispatch, external model use or product source change.

The exact sanitized failure is preserved. Sol replaced only that enum with the
configured value `neutral`, kept the possible later independent veto in the
rationale, and required a fresh passed receipt before planning.

## Population

- incidents: 398;
- corrected or explicitly contained: 398;
- open: 0;
- latest id: `AER-0398`.

The incident extends the existing
`orchestrator.parallelism_expected_leverage_vocabulary_mismatch` recurrence.
It makes no model-quality claim and changes no product, data, provider,
deployment or protected-ref authority.
