# Ariadne agent-error and correction register — revision 569

Date: 2026-08-20

Timestamp: 2026-08-20T00:41:00+10:00 (Australia/Brisbane)

## Revision scope

Revision 569 preserves AER-0659, an immediate recurrence of AER-0658. The next
register-verification command again invoked ordinary pytest, so
`tests/conftest.py` acquired the shared PostgreSQL test-schema lock before Sol
stopped the yielded session. It is rejected from acceptance and remains visible
as evidence that a remembered no-database rule is insufficient.

Every remaining test in this tranche is constrained to
`scripts.ariadne_provider_free_pytest`. The register now contains 659 incidents,
all corrected or contained and none open.

## Prevention

The immediate control is a literal provider-free-runner command allowlist. The
durable successor control is engine enforcement: a no-database work order must
reject ordinary pytest and any test whose fixture graph reaches the shared
schema before execution, rather than relying on orchestrator memory.
