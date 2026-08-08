# Ariadne agent error and correction register revision 110

Date: 2026-08-08

Status: accepted register correction

Revision 110 adds AER-0133 and brings the register to 133 bounded incidents.

## AER-0133 - expected-success rejection omitted scenario and SQLSTATE

Behavior attempt 011 passed the repaired snapshot and reached its first
expected-success scenario, but that transaction was rejected. The failure
envelope retained only `unexpected_rejection` and an empty-detail digest, so it
did not safely identify the fixed scenario or database error class.

The expected-success branch now releases only its current contract-defined
scenario id and one unambiguous valid SQLSTATE when available. The schema
allows only the twenty closed scenario identifiers. Stderr prose, SQL and
values remain closed. Another run remains ineligible pending deterministic
checks and a fresh exact-HEAD veto.
