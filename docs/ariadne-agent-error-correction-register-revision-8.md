# Ariadne agent-error register revision 8

Date: 2026-08-04

Status: A3/B3 preflight-reservation harness failure corrected

## AER-0016: preflight-blocked cost reservation was not resumable

The first occupied A3/B3 launch atomically reserved USD 0.25 for Rayleen's
primary turn, then the exact read-only cloud preflight stopped at
`impersonated_adc_refresh_failed`. No prompt, provider request, model inference,
attempt ledger, cognitive cell or product/runtime effect occurred. The parent
cost ledger nevertheless remained open, while the original `run_tranche`
entry guard rejected any later use of an existing ledger.

That fail-closed behavior prevented an unauthorized call, but it made the
authorized continuation unsafe: deleting or replacing the ledger would erase
failure evidence or reset cumulative accounting, while reserving again would
double-count Rayleen's first turn.

The correction preserves the original ledger and a closed sanitized failure
receipt bound to its SHA-256. A resume is admitted only for the canonical
ledger path when the receipt, exact open ledger, one Rayleen reservation, zero
consumed calls, zero attempt artifacts and zero runtime residue all match. The
same reservation is reused once after the existing ADC is restored and the
changed source receives a fresh exact-HEAD veto. Regression evidence proves
that two admitted primary turns finish with two total reservations, not three.

This correction grants no credential action, provider call, retry, product
access, command/write, deployment, release or protected-ref authority. Yuri
must restore the already approved keyless impersonated ADC outside the
occupied runtime before the next fresh read-only preflight.
