# Ariadne agent error and correction register — revision 357

Date: 2026-08-18

Timestamp: 2026-08-18T06:50:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 357 adds AER-0408. The second complete register-focused run passed all
population, validation and convergence-review checks and failed only the exact
residual recurring-pattern list. AER-0406 had made the asymmetric-peer-link
signature newly recurrent, but the fixture had not separated that now-owned
group into an explicit structured assertion.

The correction advances the final totals, adds explicit incident-ID checks for
all recurrence groups changed by this correction chain, regenerates the report
and requires a fresh complete run.

## Population

- incidents: 408;
- corrected or explicitly contained: 408;
- open: 0;
- latest id: `AER-0408`.

No product, data, provider, deployment or protected-ref authority changed.
