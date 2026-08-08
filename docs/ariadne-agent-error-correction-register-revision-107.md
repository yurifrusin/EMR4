# Ariadne agent error and correction register revision 107

Date: 2026-08-08

Status: accepted register correction

Revision 107 adds AER-0130 and brings the register to 130 bounded incidents.

## AER-0130 - query failure omitted its bounded site and SQLSTATE

Behavior attempt 009 closed the parent, catalogue, fixture and privilege gates,
then failed before its first scenario with only psql exit code 3. The inherited
generic helper did not retain which fixed query failed or one safe SQLSTATE.

The scenario snapshot now uses a behavior-local helper with the identical
read-only fixed-file transport. Its failure envelope can expose only the fixed
query id, one unambiguous valid SQLSTATE and a digest of that metadata. Stderr
prose and query values remain closed. Another run remains ineligible pending
deterministic tests and a fresh exact-HEAD veto.
