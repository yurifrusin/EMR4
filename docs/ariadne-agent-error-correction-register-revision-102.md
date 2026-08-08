# Ariadne agent error and correction register revision 102

Date: 2026-08-08

Status: accepted register correction

Revision 102 adds AER-0124 and brings the register to 124 bounded incidents.

## AER-0124 — touched test omitted from local format preflight

The first exact-head parse-rebind veto passed all 169 tests, contract binding,
renderer and containment checks but correctly returned `revision_required`
because one touched parse rehearsal test was not included in the local Ruff
format invocation.

The file was mechanically formatted with no behavior change. Future preflight
derives Ruff format targets from every touched Python path in the candidate,
then repeats the exact reviewer command before dispatching a fresh descendant.
