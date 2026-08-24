# Ariadne agent error and correction register — revision 662

Date: 2026-08-24

Timestamp: 2026-08-24T12:11:47.3159493+10:00 (Australia/Brisbane)

Register revision: `662`

Incident count: `1155`

Open incidents: `0`

New incidents: `AER-1154`, `AER-1155`

<!-- ariadne-agent-error-register-reading
revision: 662
incident_count: 1155
new_incident_ids: AER-1154,AER-1155
open_incident_count: 0
-->

## AER-1154

The first direct-file preflight invocation failed at import time because the
new wrapper inherited Python's `scripts/` path but did not bootstrap the
repository root. The failure occurred before the materialiser imported,
before the source root was checked, and before the sole metadata bind.

The wrapper now adds its resolved repository parent when executed outside a
package, and a focused source control preserves that behavior. The repaired
launcher passed preflight at committed source before the only bind and content
run.

Durable prevention: every new direct CLI wrapper that imports repository
packages must have an authored-synthetic direct-launch bootstrap control
before an occupied lease is consumed.

## AER-1155

The first post-run derived-fixture validation command used an incorrectly
escaped inline Python tuple and failed with an unterminated-string syntax
error. The occupied run had already completed successfully; no private
manifest, extraction or projection was reopened and no content command was
repeated.

The corrected readback used a literal PowerShell here-string piped to Python.
It validated the closed schema, canonical digest, field sets and forbidden-
value absence over the already admitted non-PHI fixture only.

Durable prevention: use literal standard-input scripts, not nested shell
quoting, for multi-string post-run JSON validation commands.
