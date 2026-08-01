# Reception One Shared Typed Language — Zero-Call Repair

Occupied lifecycle 001 failed before the one-use broker consumed its request.
The provider-call count is zero and the ledger is closed.

The cause was not model output or Vertex. The isolated cell forwarded the raw
pretty-printed `cell-request.json` (11,273 bytes), while the purpose-built relay
accepts at most 8,192 bytes. The same JSON value in canonical compact form is
6,251 bytes.

The repair changes only build-context serialization to the already canonical
broker byte representation. It does not enlarge the relay, add a channel,
change semantic content or alter any provider, identity, region, credential,
data, isolation, proofreader, output, cost or residency control.

`test_shared_cell_request_uses_compact_serialization_within_relay_cap` proves
all six supported authored-synthetic request families fit the relay cap and
that the cell receives exactly the canonical bytes. A distinct second ledger
may be opened only after every frozen repository, provider-blocked,
real-isolation, Continuity, Compass, rendered-report and ADC-control gate passes
again.
