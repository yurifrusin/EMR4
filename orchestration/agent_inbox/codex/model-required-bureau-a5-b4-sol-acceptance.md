# Sol acceptance: Bureau A5.1/B4.1 command runtimes

Date: 2026-08-05

Decision: `model_required_bureau_a5_b4_command_runtime_pass`

Accepted source HEAD: `c93bbfa7e656a97a85c5b4532525caa362c6c781`

## Acceptance basis

- Plan revision 3 and its threat-model delta freeze two separate provider-free,
  default-off, authored-synthetic command authorities.
- A5.1 check-in and B4.1 default-location focused, combined, widened regression,
  canonical fast/Bandit and disposable PostgreSQL migration gates pass.
- Sol reconciled the shared API-spine, configuration and sequential Alembic
  seams without widening either domain command.
- AER-0021 closes only through the named recovery lease; AER-0022 preserves the
  pre-admission OAuth timeout as a transport incident.
- Fresh Gemini 3.6 Flash/high reviewed exact source HEAD
  `c93bbfa7e656a97a85c5b4532525caa362c6c781`, ran 261 tests, found no material
  defect, emitted exactly one pass and left the worktree clean and unchanged.

## Decision

Accept the paired A5.1/B4.1 command-runtime descendant at its frozen local
authored-synthetic boundary. Backend identity, policy, current state,
idempotency and one atomic truth/audit/event-or-outbox unit remain authoritative;
Rayleen and Davida cannot confirm their own proposals.

No provider product runtime, patient or product-derived data, ordinary-practice
enablement, GraphQL mutation, autonomous action, external event worker, second
command family, live recovery, production, deployment, release, Pages,
protected evidence or protected ref is accepted.

The next dependency-satisfied planned lane is Bureau C4's provider-free
allowlisted-actuator simulator. Standing programme authority requires its
narrowest fail-closed descendant to be frozen and started without routine user
permission handback.
