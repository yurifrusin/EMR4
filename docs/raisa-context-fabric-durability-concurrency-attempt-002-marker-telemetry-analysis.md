# CF-D1 attempt 002 result-marker telemetry analysis

Date: 2026-08-11

Runtime source: `73cd360c68e835d8abe86846810198ee5cc9f6b7`

Reviewed harness source: `d007188c574d5c61a270a5911b4d16d3fc019d98`

## Result

Attempt 002 is rejected. It created one exact owned networkless disposable
PostgreSQL 16 container, admitted the byte-identical schema and fixtures, and
failed closed before completing `CFD1-C01` with stable code `result_marker`.
The exact container was ownership-revalidated, removed and proved absent.

The evidence records zero provider calls, product reads, product commands and
external-network operations. It is not concurrency pass evidence.

## Diagnosis boundary

The current evidence does not safely identify whether the mismatch occurred at
the `CFD1-C01` leader or its fresh replay, and it does not retain the expected or
observed allowlisted marker list. This is because `_expect_success` supplied a
bare list as failure detail and `_bounded_failure` intentionally discarded list
detail. No raw stdout, stderr, query or server text is available or required.

The evidence also reports `participant_transactions: 12`, which was a static
pass ceiling rather than an actual-attempt counter. With zero completed
scenarios it cannot support a claim that twelve participant transactions ran.
That field is rejected as attempt accounting.

## Bounded recovery

The recovery changes evidence diagnostics only:

- every result/SQLSTATE admission receives a fixed closed coordinate;
- failures may release only the coordinate, principal, isolation, exact
  allowlisted marker lists/count and safe SQLSTATE;
- a runner wrapper counts each started `_a`/`_b` participant and `_r`
  precondition transaction from its exact fixed `application_name` marker;
- pass evidence still requires exactly twelve participant and eleven
  precondition transactions;
- historical failure evidence remains schema-valid without the new optional
  precondition count; and
- attempt 003 receives a distinct immutable evidence path.

No SQL, scenario, fixture, role, isolation, transaction, wait-state,
containment, cleanup or claim contract change is authorised. A fresh clean
exact-HEAD Gemini 3.6 Flash/high veto is required before attempt 003.
