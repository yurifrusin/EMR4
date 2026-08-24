# Ariadne agent error and correction register — revision 664

Date: 2026-08-24

Timestamp: 2026-08-24T14:17:06.1781891+10:00 (Australia/Brisbane)

Register revision: `664`

Incident count: `1158`

Open incidents: `0`

New incidents: `AER-1157`, `AER-1158`

<!-- ariadne-agent-error-register-reading
revision: 664
incident_count: 1158
new_incident_ids: AER-1157,AER-1158
open_incident_count: 0
-->

## AER-1157

Three related pre-execution form and Git-control lapses were contained before
the occupied fixture read. The first candidate intent used implementation,
script and test paths in a typed authority-evidence field and failed before a
receipt. Later, PowerShell reported one cached-diff warning but did not stop the
following candidate commit because its native exit code was not explicitly
tested. An immediate descendant removed the harmless blank line. A subsequent
uncommitted incident draft then used a plausible but wrong 40-character commit
value; `git rev-parse HEAD` caught and replaced it before staging.

No wrong authority receipt or Git binding was accepted. The candidate source
used for the occupied operation was clean and machine resolved. No fixture,
archive, provider, external or protected-ref operation was repeated.

Durable prevention: authority-evidence paths use their closed document-root
form; every native precommit guard has an explicit nonzero `LASTEXITCODE` stop;
and every authored Git binding is compared with the object database before
explicit-path staging.

## AER-1158

The orchestrator directly advanced the active-operation latch after freezing
the plan even though the latch is one of the ten clockwork-owned live canonical
surfaces. The governance validator rejected the otherwise sensible edit as
`canonical_drift` before occupied execution. The published latch bytes were
restored exactly, the focused validator passed, and the full governance profile
later passed.

No fixture content had been read and no adapter, provider, external or
protected-ref action occurred while the drift existed.

Durable prevention: all ten canonical live surfaces are read-only outside the
single clockwork publication transaction; internal tranche progress remains in
plans, receipts and evidence until the clockwork writes the next named latch.
