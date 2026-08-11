# CF-D1 attempt 001 launcher failure analysis

Date: 2026-08-11

Source: `46b220284467fb3a3d5a440d7d3fa9839d4f8c28`

## Result

Attempt 001 is rejected. Direct execution stopped during Python import with
`ModuleNotFoundError` for the repository `scripts` package. The harness had not
yet entered `run_rehearsal`.

The fixed evidence path remained absent. An exact label-filtered post-failure
Docker check found zero CF-D1 containers. There were zero container starts,
database operations, participant transactions, provider calls, product reads
or external-network operations.

## Cause

The new harness imported `scripts...behavior_transaction_rehearsal` before
placing the repository root on `sys.path`. Its accepted parent already contains
the required standalone-entrypoint bootstrap, but the descendant omitted it.
Static compilation and import-from-pytest checks did not exercise the file-path
entrypoint. The exact-HEAD implementation review also passed without detecting
this mismatch.

This recurs the package-path failure family recorded by AER-0058, AER-0066,
AER-0190 and AER-0204. It is not PostgreSQL, Docker, concurrency or provider
evidence.

## Bounded correction

The correction is limited to:

- place the exact repository root on `sys.path` before importing the parent;
- retain the parent-style `# noqa: E402` import boundary;
- add a child-process test that directly invokes the script with forbidden
  caller input and proves imports complete before the fixed CLI rejection;
- move the immutable runtime evidence target to attempt 002; and
- require a fresh clean exact-HEAD Gemini 3.6 Flash/high veto before attempt
  002.

No SQL, scenario, fixture, role, transaction, wait-state, container or claim
contract changes are authorised.
