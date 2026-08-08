# Ariadne agent error and correction register revision 103

Date: 2026-08-08

Status: accepted register correction

Revision 103 adds AER-0125 and brings the register to 125 bounded incidents.

## AER-0125 — dependent catalogue digest was not rebound

The first revised-artifact parse run passed PostgreSQL parse and atomic
installation, then failed the exact catalogue comparison. The safe mismatch
digest resolves uniquely to query id `types`: its frozen digest still encoded
the former domain-level not-null flag.

Only that derived digest is replaced. Every other catalogue expectation remains
byte-identical. The contract receives a new canonical hash and another runtime
attempt remains closed until deterministic checks and a fresh exact-HEAD veto.
