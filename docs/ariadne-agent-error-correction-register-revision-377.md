# Ariadne agent error and correction register — revision 377

Date: 2026-08-18

Timestamp: 2026-08-18T13:22:34+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 377 adds AER-0429. Sol used semicolon-composed PowerShell invocations
for several pre-candidate checks and one staging/commit boundary. A later
success could therefore have masked an earlier nonzero validation exit even
though no masked failure was observed.

The exact candidate was retained unchanged. Compilation, Ruff, diff check,
103 self-contained adapter/convergence tests, 35 database-backed A5.1 tests,
85 API-Spine/plan tests and the full incident-register suite were each rerun as
independently captured processes. Every admitted gate passed. Future validation,
staging, commit and readback steps are serial command boundaries.

## Population

- incidents: 429;
- corrected or explicitly contained: 429;
- open: 0;
- latest id: `AER-0429`.

No provider, product data, deployment, release, Pages or protected-ref action
occurred. The correction changed workflow evidence only.
