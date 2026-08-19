# Check-in relay-free profile call-site and pre-registry cleanup repair report

The exact candidate at
`95d456a1e3861ae463cf3643f347fa666c75fa48` passes the deterministic repair
matrix without Docker, PostgreSQL or provider execution.

Both real container-creation call sites now pass the captured network name to
the profile predicate. A single shared helper can remove a pre-registry
container only after re-inspection proves its full ID, exact generated name,
image, harness label, owner nonce, `created` state and `Running=false`; removal
uses only the resolved full ID and must be followed by absence. Cleanup
uncertainty replaces both known and unknown primary coordinates. A cleaned
unknown controller error receives a closed server- or sidecar-specific
coordinate.

The admitted 146-test provider-free matrix passed, including 582/582 rejected
relay-free hostile mutations, the accepted Created-state suite, pure default-off
route-convergence source/continuity checks, the active-operation latch, Current
Baton and clockwork gates. Ruff, Python compilation and diff checks passed.
Tests monkeypatched the Docker boundary; the admitted matrix made zero Docker,
database or provider invocations.

An earlier 163-test standard-pytest set accidentally included the 36-case
database-backed A5.1 runtime suite and acquired the shared PostgreSQL test
schema. That run is preserved as AER-0658 process evidence and is excluded from
acceptance. It made the original tranche-wide zero-database claim false; no
attempt has been made to erase or reclassify it.

An immediate register-verification recurrence then invoked ordinary pytest and
acquired the same shared schema before interruption. AER-0659 preserves it. All
remaining closeout tests are constrained to the provider-free runner; the
recurrence demonstrates that this must become an engine rule, not a memory rule.

Attempt 003 remains immutable: its failed evidence, envelope, cleanup recovery,
historical harness blob, one occupied execution and zero automatic retries are
bound byte-exactly. This repair does not reopen attempt 003 or authorize
attempt 004.
