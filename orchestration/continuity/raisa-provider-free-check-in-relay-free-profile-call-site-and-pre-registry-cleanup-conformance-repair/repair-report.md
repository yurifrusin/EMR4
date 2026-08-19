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

The selected 163-test matrix passed, including 582/582 rejected relay-free
hostile mutations, the accepted Created-state suite, A5.1 default-off behavior,
the active-operation latch, Current Baton and clockwork gates. Ruff, Python
compilation and diff checks passed. Tests monkeypatched the Docker boundary;
the repair made zero Docker, database or provider invocations.

Attempt 003 remains immutable: its failed evidence, envelope, cleanup recovery,
historical harness blob, one occupied execution and zero automatic retries are
bound byte-exactly. This repair does not reopen attempt 003 or authorize
attempt 004.
